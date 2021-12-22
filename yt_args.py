import argparse


def get_args():
    parser =  argparse.ArgumentParser()
    parser.add_argument('url',  help="Youtube playlist URL", type=str)
    parser.parse_args()
    
    return parser

def main():
    """
        Main Function
    """
    print(f'Command line argument utility for main.py.\nTry "python yt_downloader.py -h".')


if __name__ == "__main__":
    main()