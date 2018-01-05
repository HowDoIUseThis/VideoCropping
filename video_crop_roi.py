from __future__ import print_function

import errno
import os
from textwrap import dedent

import click
import cv2


class Box(object):
    def __init__(self, value=None):
        self.value = value


def _parse_roi(start_coord, stop_coord):
    # Allows you to make the ROI in any direction, not just top left to bottom
    # right
    if start_coord == stop_coord:
        raise ValueError('start_coord == stop_coord')

    xlist, ylist = zip(start_coord, stop_coord)
    return (
        (min(xlist), min(ylist)),
        (max(xlist), max(ylist)),
    )


def crop_roi(frames, output_path):
    print(
        dedent(
            """\
            Commands:
              e - advance frame
              q - quit
              u - undo last cropped region
              r - reset cropped regions in current frame
            """,
        ),
        end='',
    )

    start_coord = Box()
    stop_coord = Box()

    # a buffer of clippings to write if committed; this holds tuples of
    # (file_path, roi_ndarray, start, stop)
    roi_write_buffer = []

    def commit_write_buffer():
        for path, roi, _, _ in roi_write_buffer:
            cv2.imwrite(path, roi)

    def drag_and_crop(event, x, y, flags, param):
        """Mouse handler function
        """
        start_coord, stop_coord = param
        if event == cv2.EVENT_LBUTTONDOWN:
            start_coord.value = x, y
        elif event == cv2.EVENT_LBUTTONUP:
            stop_coord.value = x, y
            if stop_coord.value == start_coord:
                # throw away clicks
                start_coord.value = stop_coord.value = None
        elif start_coord.value is not None and event == cv2.EVENT_MOUSEMOVE:
            start, stop = _parse_roi(start_coord.value, (x, y))
            clone = frame.copy()
            cv2.rectangle(clone, start, stop, (0, 255, 0), 2)
            cv2.imshow('Frame', clone)

    for frame_count, frame in enumerate(frames):
        clone = frame.copy()

        region_count = 0
        roi_write_buffer.clear()

        cv2.imshow('Frame', frame)
        cv2.namedWindow('Frame')

        start_coord.value = stop_coord.value = None
        cv2.setMouseCallback(
            'Frame',
            drag_and_crop,
            (start_coord, stop_coord),
        )
        cv2.waitKey(1)

        while True:
            key = cv2.waitKey(1) & 0xFF
            if start_coord.value is not None and stop_coord.value is not None:
                try:
                    start, stop = _parse_roi(
                        start_coord.value,
                        stop_coord.value,
                    )
                except ValueError:
                    # Doesn't count single mice clicks as crop regions
                    continue

                start_coord.value = stop_coord.value = None
                cv2.rectangle(frame, start, stop, (0, 255, 0), 2)
                cv2.imshow('Frame', frame)

                start_x, start_y = start
                stop_x, stop_y = stop
                roi = clone[start_y:stop_y, start_x:stop_x]
                roi_write_buffer.append((
                    os.path.join(
                        output_path,
                        'frame%d-%d.jpg' % (frame_count, region_count),
                    ),
                    roi,
                    start,
                    stop
                ))

                region_count += 1
            if key == ord('e'):
                break
            if key == ord('q'):
                commit_write_buffer()
                return
            if key == ord('u'):
                start_coord.value = stop_coord.value = None
                roi_write_buffer.pop()

                frame = clone.copy()
                for _, _, start, stop in roi_write_buffer:
                    cv2.rectangle(frame, start, stop, (0, 255, 0), 2)
                cv2.imshow('Frame', frame)
            if key == ord('r'):
                start_coord.value = stop_coord.value = None
                roi_write_buffer.clear()
                frame = clone.copy()
                cv2.imshow('Frame', frame)
                region_count = 1

        commit_write_buffer()


class CaptureContext(object):
    """An object which holds open a ``cv2.VideoCapture`` and produces an
    iterator of frames.

    Parameters
    ----------
    video_path : path-like
        The path to the video file.
    """
    def __init__(self, video_path):
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise click.FileError(
                video_path,
                hint='Is this a valid video file?',
            )

        self._frame_count = -1
        self._cropped_region_count = 0

    def __enter__(self):
        return (
            frame for _, frame in iter(self.cap.read, (False, None))
        )

    def __exit__(self, *exc_info):
        self.cap.release()
        cv2.destroyAllWindows()


@click.command()
@click.argument(
    'video',
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    '-o',
    '--output',
    type=click.Path(file_okay=False, writable=True),
    help='The path to the output directory',
    default='output',
)
@click.pass_context
def main(ctx, video, output):
    try:
        os.makedirs(output)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    with CaptureContext(video) as frames:
        crop_roi(frames, output)


if __name__ == '__main__':
    main()
