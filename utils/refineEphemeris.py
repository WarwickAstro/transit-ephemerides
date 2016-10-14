"""
Script to quickly refine an object's ephemeris

Assumes the Tmid is ok and works out the new
period. Use the script if a partial is obtained
when a full transit is expected. Estimate the mid
point and update the target's ephem for next time
"""
import argparse as ap
from math import ceil

def argParse():
    parser = ap.ArgumentParser()
    parser.add_argument('epoch', help='Epoch', type=float)
    parser.add_argument('period', help='Period', type=float)
    parser.add_argument('t_new', help='t_mid of new transit', type=float)
    return parser.parse_args()

if __name__ == "__main__":
    args = argParse()
    t_diff = args.t_new - args.epoch 
    n_cycles = t_diff / args.period
    period_new = t_diff / ceil(n_cycles)
    print('NEW EPHEM: E={} P={}'.format(round(args.epoch, 6), round(period_new, 6)))
