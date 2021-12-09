
def guessIntrinsics(frame_width, frame_height):
    # SetCameraIntrinsics
    # If optical centers are not defined just use center of image
    cx = frame_width / 2.0
    cy = frame_height / 2.0
    fx = 500.0 * (frame_width / 640.0)
    fy = 500.0 * (frame_height / 480.0)

    fx = (fx + fy) / 2.0
    fy = fx

    return (fx, fy, cx, cy)
