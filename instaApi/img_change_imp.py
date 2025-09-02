from instagrapi import Client
from pathlib import Path
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('n', type=int, nargs=1, help='an integer for the accumulator')
    args = parser.parse_args()
    print("Changing now...")
    try:
        cl = Client()
        cl.login("justin.sapun", "redroom87")
        img = "./images/"+str(args.n[0])+".jpg"
        img_path = Path(img)
        print(img_path)
        cl.account_change_picture(img_path)
        print("Changed")
    except:
        print("Failed to change pfp")
