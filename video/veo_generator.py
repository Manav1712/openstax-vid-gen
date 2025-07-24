import os
import time
import requests
import json
from typing import Dict, Optional, List
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

class VeoVideoGenerator:
    """
    Google Veo 2 video generator via real Gemini API for educational videos.
    Creates 5-8 second, 720p educational videos with cinematic quality.
    
    Features:
    - 720p resolution at 24fps
    - 5-8 second duration optimized for educational content
    - Cinematic quality with professional video effects
    - Silent video (audio can be added separately)
    - Text-to-video and image-to-video capabilities
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Veo video generator.
        
        Args:
            api_key: Google API key for Gemini (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key not found. Set GOOGLE_API_KEY environment variable.")
        
        # Configure Gemini API client for Veo 2
        self.client = genai.Client(api_key=self.api_key)
        
        # Default video configuration for educational content
        self.default_config = {
            "resolution": "720p",         # Veo 2 standard resolution
            "duration": "5-8s",           # Veo 2 variable duration
            "style": "cinematic",         # Professional educational look
            "audio": "silent",            # Veo 2 creates silent videos
            "aspect_ratio": "16:9",       # Standard widescreen
            "frame_rate": "24fps"         # Cinematic frame rate
        }
        
        # Educational video prompting guidelines
        self.edu_guidelines = {
            "camera_work": [
                "smooth transitions", "dynamic but stable shots", 
                "close-ups for details", "wide shots for context"
            ],
            "lighting": [
                "bright, clear lighting", "soft shadows", 
                "educational environment", "professional appearance"
            ],
            "pacing": [
                "clear demonstrations", "step-by-step visuals",
                "engaging but focused", "digestible information"
            ]
        }
    
    def script_to_veo_prompt(self, script: str) -> str:
        """
        Convert structured educational script to optimized Veo prompt.
        
        Args:
            script: Formatted script from LLM explainer
            
        Returns:
            Optimized prompt string for Veo generation
        """
        # Parse script sections (reuse from explainer.py)
        sections = self._parse_script_sections(script)
        
        # Build Veo-optimized prompt
        prompt_parts = []
        
        # Core scene description
        if sections.get('SCENE'):
            prompt_parts.append(f"Setting: {sections['SCENE']}")
        
        # Visual actions and demonstrations
        if sections.get('VISUAL_ACTION'):
            prompt_parts.append(f"Action: {sections['VISUAL_ACTION']}")
        
        # Camera work for cinematic quality
        if sections.get('CAMERA'):
            prompt_parts.append(f"Camera: {sections['CAMERA']}")
        
        # Audio and narration
        if sections.get('NARRATION'):
            prompt_parts.append(f'Narration: "{sections["NARRATION"]}"')
        
        if sections.get('AUDIO'):
            prompt_parts.append(f"Audio: {sections['AUDIO']}")
        
        # Add educational video optimizations
        educational_enhancements = [
            "Style: Professional educational video, cinematic quality",
            "Quality: 4K resolution, smooth motion, clear details",
            "Pace: Engaging but educational, clear demonstrations",
            "Duration: 30 seconds"
        ]
        
        prompt_parts.extend(educational_enhancements)
        
        return ". ".join(prompt_parts)
    
    def _parse_script_sections(self, script: str) -> Dict[str, str]:
        """Parse structured script into sections."""
        sections = {'SCENE': '', 'NARRATION': '', 'VISUAL_ACTION': '', 'CAMERA': '', 'AUDIO': ''}
        
        lines = script.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('SCENE:'):
                current_section = 'SCENE'
                sections[current_section] = line[6:].strip()
            elif line.startswith('NARRATION:'):
                current_section = 'NARRATION'
                sections[current_section] = line[10:].strip()
            elif line.startswith('VISUAL_ACTION:'):
                current_section = 'VISUAL_ACTION'
                sections[current_section] = line[14:].strip()
            elif line.startswith('CAMERA:'):
                current_section = 'CAMERA'
                sections[current_section] = line[7:].strip()
            elif line.startswith('AUDIO:'):
                current_section = 'AUDIO'
                sections[current_section] = line[6:].strip()
            elif current_section and line:
                sections[current_section] += ' ' + line
        
        return sections
    
    def create_video(self, script: str, wait_for_completion: bool = True) -> Dict:
        """
        Generate educational video using REAL Veo 2 API.
        
        Args:
            script: Educational script from LLM explainer
            wait_for_completion: Whether to wait for video generation
            
        Returns:
            Dictionary with video generation result and URL
        """
        try:
            # Convert script to Veo-optimized prompt
            veo_prompt = self.script_to_veo_prompt(script)
            
            print(f"🎬 Creating REAL Veo 2 video with prompt...")
            print(f"📝 Prompt: {veo_prompt[:200]}...")
            
            # REAL Veo 2 API call (stable model, no billing required)
            operation = self.client.models.generate_videos(
                model="veo-2.0-generate-001",
                prompt=veo_prompt,
                config=types.GenerateVideosConfig(
                    negative_prompt="cartoon, low quality, blurry, distorted",
                    aspect_ratio="16:9",
                    person_generation="allow_adult"
                ),
            )
            
            print(f"✅ Veo 2 video generation started!")
            print(f"Operation ID: {operation.name}")
            
            video_result = {
                "success": True,
                "operation_id": operation.name,
                "status": "processing",
                "prompt": veo_prompt,
                "estimated_completion": "1-6 minutes",
                "duration": "5-8 seconds",
                "resolution": "720p",
                "aspect_ratio": "16:9",
                "audio": "silent_video",
                "operation": operation,
                "video_filename": None  # Will be populated when complete
            }
            
            if wait_for_completion:
                return self._wait_for_real_completion(operation, video_result)
            
            return video_result
            
        except Exception as e:
            print(f"❌ Veo 2 video generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Video generation error: {str(e)}",
                "prompt": veo_prompt if 'veo_prompt' in locals() else script
            }
    
    def _wait_for_real_completion(self, operation, initial_result: Dict) -> Dict:
        """
        Wait for REAL Veo 2 video completion with polling.
        """
        print("⏳ Waiting for REAL Veo 2 video generation...")
        
        # Poll the operation until completion (official Google docs polling)
        while not operation.done:
            print("Waiting for video generation to complete...")
            time.sleep(10)  # Official recommended polling interval
            operation = self.client.operations.get(operation)
        
        # Handle completion
        if operation.done and operation.response:
            print("✅ Veo 2 video generation completed!")
            
            # Download and save the video (following official API docs)
            generated_video = operation.response.generated_videos[0]
            video_filename = f"educational_video_{int(time.time())}.mp4"
            
            # Download the video file
            self.client.files.download(file=generated_video.video)
            generated_video.video.save(video_filename)
            
            # Update result with real completion data
            initial_result.update({
                "status": "completed",
                "video_filename": video_filename,
                "completion_time": time.time(),
                "duration": "5-8 seconds",
                "resolution": "720p",
                "format": "MP4",
                "audio": "silent_video",
                "file_size": os.path.getsize(video_filename) if os.path.exists(video_filename) else "Unknown"
            })
            
            print(f"✅ Educational video saved as: {video_filename}")
            
        else:
            # Handle failure
            error_msg = f"Video generation failed: {operation.error if hasattr(operation, 'error') else 'Unknown error'}"
            initial_result.update({
                "status": "failed",
                "error": error_msg
            })
            print(f"❌ {error_msg}")
        
        return initial_result
    
    def check_video_status(self, operation_id: str) -> Dict:
        """
        Check status of Veo 2 video generation.
        
        Args:
            operation_id: Video generation operation ID
            
        Returns:
            Current status and progress information
        """
        try:
            operation = self.client.operations.get(operation_id)
            
            return {
                "success": True,
                "operation_id": operation_id,
                "status": "completed" if operation.done else "processing",
                "done": operation.done,
                "has_response": hasattr(operation, 'response') and operation.response is not None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Status check failed: {str(e)}"
            }
    
    def get_video_info(self, video_filename: str) -> Dict:
        """
        Get information about generated Veo 2 video.
        
        Args:
            video_filename: Local filename of generated video
            
        Returns:
            Video metadata and information
        """
        return {
            "filename": video_filename,
            "resolution": "720p (1280x720)",
            "duration": "5-8 seconds",
            "format": "MP4 (H.264)",
            "audio": "Silent (audio can be added separately)",
            "frame_rate": "24fps",
            "file_size": os.path.getsize(video_filename) if os.path.exists(video_filename) else "Unknown",
            "quality": "Professional educational video"
        }


def test_veo_generator():
    """
    Test function for Veo 2 video generator.
    """
    print("=== Testing Google Veo 2 Video Generator ===")
    
    try:
        # Initialize generator
        generator = VeoVideoGenerator()
        print("✅ Veo 2 generator initialized (stable model)")
        
        # Test with educational physics script optimized for Veo 2
        test_script = """SCENE: Clean, modern physics laboratory with demonstration equipment and clear lighting
NARRATION: Accuracy measures how close your measurement is to the true value, while precision shows consistency.
VISUAL_ACTION: Split screen showing dart board demonstration - accurate shots hitting bullseye center, precise shots grouping tightly together
CAMERA: Medium shot transitioning to close-up of measurement demonstration with smooth dolly movement
AUDIO: Clear educational narration with subtle laboratory ambient sounds"""
        
        print(f"\n📝 Educational Test Script:")
        print(test_script)
        
        # Convert to Veo 2 prompt
        veo_prompt = generator.script_to_veo_prompt(test_script)
        print(f"\n🎯 Veo 2 Prompt:")
        print(f'"{veo_prompt}"')
        
        # Test video creation
        print(f"\n🎬 Creating REAL educational video with Veo 2...")
        result = generator.create_video(test_script, wait_for_completion=True)
        
        if result["success"]:
            print(f"\n✅ Veo 2 video generation successful!")
            print(f"Operation ID: {result['operation_id']}")
            print(f"Status: {result['status']}")
            print(f"Duration: {result['duration']}")
            print(f"Resolution: {result['resolution']}")
            print(f"Audio: {result['audio']}")
            
            if result.get('video_filename'):
                print(f"Local file: {result['video_filename']}")
                print(f"File size: {result.get('file_size', 'Unknown')}")
                
                print(f"\n🎉 SUCCESS! Your educational video is ready!")
                print(f"📱 Play the video: {result['video_filename']}")
                print(f"💡 Note: Video is silent - you can add narration separately")
        else:
            print(f"❌ Video generation failed: {result['error']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    test_veo_generator() 