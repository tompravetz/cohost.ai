import time
import sys
import logging
import os
from typing import Optional, Dict, Any

try:
    from obswebsocket import obsws, requests
except ImportError:
    raise ImportError("obs-websocket-py package not found. Please install it with: pip install obs-websocket-py")

logger = logging.getLogger(__name__)

class OBSWebsocketsManager:
    """Manager for OBS WebSocket connections and operations."""

    def __init__(self, host: str = None, port: int = None, password: str = None):
        """
        Initialize OBS WebSocket connection.

        Args:
            host: OBS WebSocket host (default: localhost)
            port: OBS WebSocket port (default: 4455)
            password: OBS WebSocket password (default: from env var)
        """
        self.host = host or os.getenv('OBS_HOST', 'localhost')
        self.port = port or int(os.getenv('OBS_PORT', '4455'))
        self.password = password or os.getenv('OBS_PASSWORD', 'ZPpGrnxDm1pXYwgS')
        self.ws: Optional[obsws] = None
        self.connected = False

        self._connect()

    def _connect(self):
        """Establish connection to OBS WebSocket."""
        try:
            self.ws = obsws(self.host, self.port, self.password)
            self.ws.connect()
            self.connected = True
            logger.info(f"Connected to OBS WebSocket at {self.host}:{self.port}")
        except Exception as e:
            error_msg = f"Failed to connect to OBS WebSocket: {e}"
            logger.error(error_msg)
            print(f"\nERROR: {error_msg}")
            print("Please ensure:")
            print("1. OBS is running")
            print("2. WebSocket server is enabled in OBS")
            print("3. Connection details are correct")
            raise ConnectionError(error_msg)

    def disconnect(self):
        """Disconnect from OBS WebSocket."""
        if self.ws and self.connected:
            try:
                self.ws.disconnect()
                self.connected = False
                logger.info("Disconnected from OBS WebSocket")
            except Exception as e:
                logger.error(f"Error disconnecting from OBS: {e}")

    def _ensure_connected(self):
        """Ensure we have a valid connection to OBS."""
        if not self.connected or not self.ws:
            raise ConnectionError("Not connected to OBS WebSocket")

    def set_scene(self, new_scene: str):
        """Set the current scene in OBS."""
        try:
            self._ensure_connected()
            self.ws.call(requests.SetCurrentProgramScene(sceneName=new_scene))
            logger.debug(f"Set scene to: {new_scene}")
        except Exception as e:
            logger.error(f"Failed to set scene '{new_scene}': {e}")
            raise

    def set_filter_visibility(self, source_name: str, filter_name: str, filter_enabled: bool = True):
        """Set the visibility of a source's filter."""
        try:
            self._ensure_connected()
            self.ws.call(requests.SetSourceFilterEnabled(
                sourceName=source_name,
                filterName=filter_name,
                filterEnabled=filter_enabled
            ))
            logger.debug(f"Set filter '{filter_name}' on '{source_name}' to {filter_enabled}")
        except Exception as e:
            logger.error(f"Failed to set filter visibility: {e}")
            raise

    def set_source_visibility(self, scene_name: str, source_name: str, source_visible: bool = True):
        """Set the visibility of a source in a scene."""
        try:
            self._ensure_connected()
            response = self.ws.call(requests.GetSceneItemId(sceneName=scene_name, sourceName=source_name))
            item_id = response.datain['sceneItemId']
            self.ws.call(requests.SetSceneItemEnabled(
                sceneName=scene_name,
                sceneItemId=item_id,
                sceneItemEnabled=source_visible
            ))
            logger.debug(f"Set source '{source_name}' in scene '{scene_name}' to {source_visible}")
        except Exception as e:
            logger.error(f"Failed to set source visibility: {e}")
            raise

    # Returns the current text of a text source
    def get_text(self, source_name):
        response = self.ws.call(requests.GetInputSettings(inputName=source_name))
        return response.datain["inputSettings"]["text"]

    # Returns the text of a text source
    def set_text(self, source_name, new_text):
        self.ws.call(requests.SetInputSettings(inputName=source_name, inputSettings = {'text': new_text}))

    def get_source_transform(self, scene_name, source_name):
        response = self.ws.call(requests.GetSceneItemId(sceneName=scene_name, sourceName=source_name))
        myItemID = response.datain['sceneItemId']
        response = self.ws.call(requests.GetSceneItemTransform(sceneName=scene_name, sceneItemId=myItemID))
        transform = {}
        transform["positionX"] = response.datain["sceneItemTransform"]["positionX"]
        transform["positionY"] = response.datain["sceneItemTransform"]["positionY"]
        transform["scaleX"] = response.datain["sceneItemTransform"]["scaleX"]
        transform["scaleY"] = response.datain["sceneItemTransform"]["scaleY"]
        transform["rotation"] = response.datain["sceneItemTransform"]["rotation"]
        transform["sourceWidth"] = response.datain["sceneItemTransform"]["sourceWidth"] # original width of the source
        transform["sourceHeight"] = response.datain["sceneItemTransform"]["sourceHeight"] # original width of the source
        transform["width"] = response.datain["sceneItemTransform"]["width"] # current width of the source after scaling, not including cropping. If the source has been flipped horizontally, this number will be negative.
        transform["height"] = response.datain["sceneItemTransform"]["height"] # current height of the source after scaling, not including cropping. If the source has been flipped vertically, this number will be negative.
        transform["cropLeft"] = response.datain["sceneItemTransform"]["cropLeft"] # the amount cropped off the *original source width*. This is NOT scaled, must multiply by scaleX to get current # of cropped pixels
        transform["cropRight"] = response.datain["sceneItemTransform"]["cropRight"] # the amount cropped off the *original source width*. This is NOT scaled, must multiply by scaleX to get current # of cropped pixels
        transform["cropTop"] = response.datain["sceneItemTransform"]["cropTop"] # the amount cropped off the *original source height*. This is NOT scaled, must multiply by scaleY to get current # of cropped pixels
        transform["cropBottom"] = response.datain["sceneItemTransform"]["cropBottom"] # the amount cropped off the *original source height*. This is NOT scaled, must multiply by scaleY to get current # of cropped pixels
        return transform

    # The transform should be a dictionary containing any of the following keys with corresponding values
    # positionX, positionY, scaleX, scaleY, rotation, width, height, sourceWidth, sourceHeight, cropTop, cropBottom, cropLeft, cropRight
    # e.g. {"scaleX": 2, "scaleY": 2.5}
    # Note: there are other transform settings, like alignment, etc, but these feel like the main useful ones.
    # Use get_source_transform to see the full list
    def set_source_transform(self, scene_name, source_name, new_transform):
        response = self.ws.call(requests.GetSceneItemId(sceneName=scene_name, sourceName=source_name))
        myItemID = response.datain['sceneItemId']
        self.ws.call(requests.SetSceneItemTransform(sceneName=scene_name, sceneItemId=myItemID, sceneItemTransform=new_transform))

    # Note: an input, like a text box, is a type of source. This will get *input-specific settings*, not the broader source settings like transform and scale
    # For a text source, this will return settings like its font, color, etc
    def get_input_settings(self, input_name):
        return self.ws.call(requests.GetInputSettings(inputName=input_name))

    # Get list of all the input types
    def get_input_kind_list(self):
        return self.ws.call(requests.GetInputKindList())

    # Get list of all items in a certain scene
    def get_scene_items(self, scene_name):
        return self.ws.call(requests.GetSceneItemList(sceneName=scene_name))


if __name__ == '__main__':

    print("Connecting to OBS Websockets")
    obswebsockets_manager = OBSWebsocketsManager()

    print("Changing visibility on a source \n\n")
    obswebsockets_manager.set_source_visibility('*** Mid Monitor', "Elgato Cam Link", False)
    time.sleep(3)
    obswebsockets_manager.set_source_visibility('*** Mid Monitor', "Elgato Cam Link", True)
    time.sleep(3)

    print("\nEnabling filter on a scene...\n")
    time.sleep(3)
    obswebsockets_manager.set_filter_visibility("/// TTS Characters", "Move Source - Godrick - Up", True)
    time.sleep(3)
    obswebsockets_manager.set_filter_visibility("/// TTS Characters", "Move Source - Godrick - Down", True)
    time.sleep(5)

    print("Swapping scene!")
    obswebsockets_manager.set_scene('*** Camera (Wide)')
    time.sleep(3)
    print("Swapping back! \n\n")
    obswebsockets_manager.set_scene('*** Mid Monitor')

    print("Changing visibility on scroll filter and Audio Move filter \n\n")
    obswebsockets_manager.set_filter_visibility("Line In", "Audio Move - Chat God", True)
    obswebsockets_manager.set_filter_visibility("Middle Monitor", "DS3 - Scroll", True)
    time.sleep(3)
    obswebsockets_manager.set_filter_visibility("Line In", "Audio Move - Chat God", False)
    obswebsockets_manager.set_filter_visibility("Middle Monitor", "DS3 - Scroll", False)

    print("Getting a text source's current text! \n\n")
    current_text = obswebsockets_manager.get_text("??? Challenge Title ???")
    print(f"Here's its current text: {current_text}\n\n")

    print("Changing a text source's text! \n\n")
    obswebsockets_manager.set_text("??? Challenge Title ???", "Here's my new text!")
    time.sleep(3)
    obswebsockets_manager.set_text("??? Challenge Title ???", current_text)
    time.sleep(1)

    print("Getting a source's transform!")
    transform = obswebsockets_manager.get_source_transform('*** Mid Monitor', "Middle Monitor")
    print(f"Here's the transform: {transform}\n\n")

    print("Setting a source's transform!")
    new_transform = {"scaleX": 2, "scaleY": 2}
    obswebsockets_manager.set_source_transform('*** Mid Monitor', "Middle Monitor", new_transform)
    time.sleep(3)
    print("Setting the transform back. \n\n")
    obswebsockets_manager.set_source_transform('*** Mid Monitor', "Middle Monitor", transform)

    response = obswebsockets_manager.get_input_settings("??? Challenge Title ???")
    print(f"\nHere are the input settings:{response}\n")
    time.sleep(2)

    response = obswebsockets_manager.get_input_kind_list()
    print(f"\nHere is the input kind list:{response}\n")
    time.sleep(2)

    response = obswebsockets_manager.get_scene_items('*** Mid Monitor')
    print(f"\nHere is the scene's item list:{response}\n")
    time.sleep(2)

    time.sleep(300)

#############################################