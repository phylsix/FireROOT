#!/usr/bin/env python
from __future__ import print_function
import os, json, ROOT
from collections import OrderedDict
from rootpy.io import root_open
from rootpy.plotting.style import set_style
from rootpy.plotting import Hist, Legend, Canvas

from FireROOT.Analysis.Utils import *

fn = os.path.join(os.getenv('CMSSW_BASE'), 'src/FireROOT/Analysis/python/outputs/rootfiles/leptonjetTrackTrackDCA.root')
outdir = os.path.join(os.getenv('CMSSW_BASE'), 'src/FireROOT/Analysis/python/etc/plots/leptonjetTrackTrackDCACutEfficiency')
if not os.path.isdir(outdir): os.makedirs(outdir)

set_style(MyStyle())
c = Canvas()

f=root_open(fn)

def routine(chan, var, title):
    hs=[]
    chandir = getattr(f, 'ch'+chan)

    effs=OrderedDict()
    for t in chandir.sig.keys():
        sigtag = t.name
        h = getattr(getattr(chandir.sig, sigtag), var) # Hist
        h_total = h.integral(overflow=True)

        h_ = h.clone()
        for i in range(1, h.nbins()+1):
            h_[i] = h.integral(1, xbin2=i)/h_total
            h_[i].error = 0
            if i==50: effs[sigtag] = h.integral(1, xbin2=i)/h_total
        h_.title = sigtag
        h_.drawstyle = 'PLC hist'
        h_.legendstyle='L'
        hs.append(h_)
    mineff = min(effs.values())
    aveeff = sum(effs.values())/len(effs)
    effs['sig_ave'] = aveeff
    effs['sig_min'] = mineff

    h = getattr(chandir.data, var)
    h_total = h.integral(overflow=True)
    if h_total!=0:
        h_ = h.empty_clone()
        for i in range(1, h.nbins()+1):
            h_[i] = h.integral(1, xbin2=i)/h_total
            h_[i].error = 0
            if i==50: effs['data'] = h.integral(1, xbin2=i)/h_total
        h_.drawstyle = 'hist'
        h_.title='data'
        h_.color = 'black'
        h_.linestyle = 'dashed'
        h_.legendstyle='L'
        h_.linewidth=2
        hs.append(h_)


    print('>',chan, var)
    maxlen = max([len(k) for k in effs])
    for k in effs:
        fmt = '{:%d}:{:.2f}'%(maxlen+2)+'%'
        print(fmt.format(k, effs[k]*100))


    legend = Legend(hs, pad=c, margin=0.1, topmargin=0.02, entryheight=0.02, textsize=12)
    axes, limits =draw(hs, ylimits=(0., 1.05), ytitle='(backward) cut efficiency',)
    legend.Draw()
    title = TitleAsLatex('[{}] '.format(chan.replace('mu', '#mu'))+title)
    title.Draw()
    draw_labels('59.74 fb^{-1} (13 TeV)', cms_position='left', extra_text='work-in-progress')
    ROOT.gPad.SetGrid()

    c.SaveAs('{}/ch{}_{}.pdf'.format(outdir, chan, var))
    c.Clear()

for chan in ['2mu2e', '4mu']:
    routine(chan, 'tktkdca', 'leptonjet TrackTrack DCA cut efficiency')
    routine(chan, 'tktkdca_after_drcosmic', 'leptonjet TrackTrack DCA (#DeltaR_{cosmic}>0.05) cut efficiency')
    routine(chan, 'maxabstkdz', 'leptonjet max track |dz| cut efficiency')
    routine(chan, 'maxabstkdz_after_drcosmic', 'leptonjet max track |dz| (#DeltaR_{cosmic}>0.05) cut efficiency')
f.close()