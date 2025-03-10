import cv2
import imageio
import sys

def convert_to_timestamped_gif(input_path, output_path='output.gif', gif_fps=10, resize_scale=None):
    # Open the video file
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("Error: Could not open video file")
        return

    # Get video properties
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Calculate frame skip interval to match desired GIF FPS
    frame_skip = max(1, int(video_fps / gif_fps))
    
    # Store processed frames
    frames = []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_skip == 0:
            # Calculate current time
            current_time = frame_count / video_fps
            minutes = int(current_time // 60)
            seconds = current_time % 60
            timestamp = f"{minutes:02d}:{seconds:06.3f}"

            # Add timestamp to frame
            cv2.putText(frame, timestamp, (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                        (255, 255, 255), 2, cv2.LINE_AA)

            # Resize if specified
            if resize_scale:
                frame = cv2.resize(frame, resize_scale)

            # Convert BGR to RGB and add to frames list
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        frame_count += 1

    cap.release()

    # Save as optimized GIF
    if frames:
        imageio.mimsave(output_path, frames, fps=gif_fps, subrectangles=True)
        print(f"Successfully created GIF: {output_path}")
    else:
        print("Error: No frames processed")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python video_to_gif.py <input_video> [output_gif] [width] [height]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'output.gif'
    resize_scale = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else None
    
    convert_to_timestamped_gif(input_path, output_path, resize_scale=resize_scale)