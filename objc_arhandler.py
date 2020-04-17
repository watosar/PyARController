from rubicon.objc import *
from rubicon.objc.runtime import load_library, send_super

load_library('UIKit')
load_library('SceneKit')
load_library('ARKit')

ARSessionObserver = ObjCProtocol('ARSessionObserver')

ARSession = ObjCClass('ARSession')
ARPositionalTrackingConfiguration = ObjCClass('ARPositionalTrackingConfiguration')
UIApplication = ObjCClass('UIApplication')

ARSessionRunOptionResetTracking = (1 << 0)

ARTrackingStateNotAvailable = 0
ARTrackingStateLimited = 1
ARTrackingStateNormal = 2

ARTrackingStateReasonNone = 0
ARTrackingStateReasonInitializing = 1
ARTrackingStateReasonRelocalizing = 2
ARTrackingStateReasonExcessiveMotion = 3
ARTrackingStateReasonInsufficientFeatures = 4


class ARSessionHandler(NSObject, protocols=[ARSessionObserver]):
    @objc_method
    def init(self):
        self = ObjCInstance(send_super(__class__, self, 'init'))
        self.session = ARSession.new()
        return self
    
    # start ar session
    @objc_method
    def start(self):
        self.did_update_session_info('Initializing AR session.')
        # only position tracking
        configuration = ARPositionalTrackingConfiguration.new()
        self.session.runWithConfiguration_(configuration)

        # Set a delegate to track the number of plane anchors for providing UI feedback.
        self.session.delegate = self
        
        #Prevent the screen from being dimmed after a while as users will likely
        #have long periods of interaction without touching the screen or buttons.
        UIApplication.sharedApplication.setIdleTimerDisabled_(True)
        

    @objc_method
    def pause(self):
        print('pause')
        # Pause the view's AR session.
        self.session.pause()

    @objc_method
    def session_cameraDidChangeTrackingState_(self, session, camera) ->  None:
        self.updateSessionInfoForFrame_trackingState_andReason_(session.currentFrame, camera.trackingState, camera.trackingStateReason)

    @objc_method
    def sessionWasInterrupted_(self, session) ->  None:
        # Inform the user that the session has been interrupted, for example, by presenting an overlay.
        self.did_update_session_info('Session was interrupted')

    @objc_method
    def sessionInterruptionEnded_(self, session) -> None:
        # Reset tracking and/or remove existing anchors if consistent tracking is required.
        self.resetTracking()
        self.did_update_session_info('Session interruption ended')
    
    @objc_method
    def session_didFailWithError_(self, session, error) -> None:
        sessionInfo = ns_from_py(f"Session failed: {py_from_ns(error.localizedDescription)}")
        if not error: return 
        
        errorWithInfo = error
        messages = [
            errorWithInfo.localizedDescription,
            errorWithInfo.localizedFailureReason,
            errorWithInfo.localizedRecoverySuggestion
        ]
        
        # Remove optional error messages.
        #errorMessage = messages.compactMap({ $0 }).joined(separator: "\n")
        errorMessage = '\n'.join(py_from_ns(i) for i in messages)
        self.did_fail_with_error(errorMessage)
    
    @objc_method
    def updateSessionInfoForFrame_trackingState_andReason_(self, frame, trackingState, trackingStateReason) -> None:
        # Update the UI to provide feedback on the state of the AR experience.
        message = {
            ARTrackingStateNormal: 
                "Move the device around to detect horizontal and vertical surfaces." if not frame.anchors.count else "",
            ARTrackingStateNotAvailable: 
                "Tracking unavailable.",
            ARTrackingStateLimited:
                {
                    ARTrackingStateReasonInitializing: 
                        "Initializing AR session.",
                    ARTrackingStateReasonRelocalizing:
                        "The AR session is attempting to resume after an interruption.",
                    ARTrackingStateReasonExcessiveMotion:
                        "Tracking limited - Move the device more slowly.",
                    ARTrackingStateReasonInsufficientFeatures:
                        "Tracking limited - Point the device at an area with visible surface detail, or improve lighting conditions."
                }.get(trackingStateReason, '')
        }.get(trackingState, '')
        self.did_update_session_info(message)
    
    def did_update_session_info(self, info):
        pass
    
    def did_fail_with_error(self, errorMessage):
        print(errorMessage)
        self.resetTracking()

    @objc_method
    def resetTracking(self) -> None:
        configuration = ARPositionalTrackingConfiguration.new()
        self.session.runWithConfiguration_options_(configuration, options=ARSessionRunOptionResetTracking)

