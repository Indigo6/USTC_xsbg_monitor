import argparse
import logging


def fmt_time(dtime):
    if dtime <= 0:
        return '0:00.000'
    elif dtime < 60:
        return '0:%02d.%03d' % (int(dtime), int(dtime * 1000) % 1000)
    elif dtime < 3600:
        return '%d:%02d.%03d' % (int(dtime / 60), int(dtime) % 60, int(dtime * 1000) % 1000)
    else:
        return '%d:%02d:%02d.%03d' % (int(dtime / 3600), int((dtime % 3600) / 60), int(dtime) % 60,
                                      int(dtime * 1000) % 1000)


def create_logger(log_path):
    head = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename=log_path,
                        filemode='w',
                        format=head)
    logger = logging.getLogger('')
    logger.setLevel(logging.INFO)

    console = logging.StreamHandler()
    logging.getLogger('').addHandler(console)

    return logger


def parse_args():
    parser = argparse.ArgumentParser(description='Train keypoints network')
    # general
    parser.add_argument('--cfg',
                        help='experiment configure file name',
                        default='cfg/config.json',
                        type=str)
    args = parser.parse_args()
    return args
