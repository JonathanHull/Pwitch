#!/usr/bin/env python3

import argparse
import signal
import json
import sys
import os

from pwitch import PwitchClient
from pwitch.PwitchServer import PwitchServer

## Use signal to handle kill signal passed by docker for graceful shutdown.

def argument_parser(args):
    parser = argparse.ArgumentParser(description="Pwitch IRC bot service")

    parser.add_argument("service", 
        help="start specified service.\nOptions are: server|client",
        type=str, choices=['server','client'])

    parser.add_argument("--options", help="Specify json options file.\n"+
        "Default: cfg/cfg.json", type=str, default=cfg_dir+"cfg.json")
            
    parser.add_argument("--irc-list", help="Specify json file containing IRC"+
        " channels.", type=str, default=None)

    return parser.parse_args(args)

def main():
    ## Bot / Client settings
    if args.service == "server":
        irc_channels = cfg["channels"]
        global PwitchMaster
        PwitchMaster = PwitchServer(cfg, irc_channels)
        PwitchMaster.start()
        print("Press Ctrl+C to exit")

    elif args.service == "client":
        os.environ['chatBuffer'] = "yes"
        x = PwitchClient(cfg["nick"], cfg["oauth"], cfg["channel"],
            userBuffer=True)
        x.start()

    ## Signal handling for Docker.
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


def signal_handler(sig, frame):
    print("\n[SERVER] Disconnecting")
    PwitchMaster.stop_processes()
    sys.exit(0)

if __name__ == "__main__":
    cfg_dir = os.path.dirname(os.path.abspath(__file__))+"/cfg/"
    args = argument_parser(sys.argv[1:])

    try:
        with open(args.options) as w:
            cfg = json.load(w)
    except:
        print("Unable to load options. Have you deleted or changed the package"+
            "filestructure?")

    main()
