from argparse import ArgumentParser
from gearbest_scraper import scraper


def main():

    parser = ArgumentParser()

    parser.add_argument('--mode', type=str, default='search', 
    help='choose a method to Gearbest_Scraper')
    parser.add_argument('--config', type=str, default='configuration.json', 
    help='configuration file ex: configuration.json')

    args = parser.parse_args()

    scraper.run(args.config, args.mode)


if __name__ == '__main__':
    main()

