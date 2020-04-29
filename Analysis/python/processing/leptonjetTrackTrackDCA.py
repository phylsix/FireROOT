#!/usr/bin/env python
from FireROOT.Analysis.Events import *
from FireROOT.Analysis.Utils import *

class MyEvents(CosmicEvents):
    def __init__(self, files=None, type='MC', maxevents=-1, channel=['2mu2e', '4mu'], **kwargs):
        super(MyEvents, self).__init__(files=files,
                                       type=type, maxevents=maxevents, channel=channel, **kwargs)

    def processEvent(self, event, aux):
        if aux['channel'] not in self.Channel: return
        flag = False
        if aux['hasCosmicShower'] and self.Type=='DATA': flag=True
        if not aux['hasCosmicShower'] and self.Type!='DATA': flag=True
        if flag is False: return

        chan = aux['channel']
        LJ0, LJ1 = aux['lj0'], aux['lj1']
        self.Histos['{}/grandcosmicvetores'.format(chan)].Fill(0, aux['wgt'])
        passAllCosmicVeto = True
        for lj in [LJ0, LJ1]:

            if passAllCosmicVeto and not lj.passCosmicVeto(event): passAllCosmicVeto=False

            if lj.minTwoTrackDist()<0: continue ## meaning <2 tracks
            self.Histos['{}/tktkdca'.format(chan)].Fill(lj.minTwoTrackDist(), aux['wgt'])

            if passAllCosmicVeto and lj.minTwoTrackDist()>20: passAllCosmicVeto=False

            if lj.passCosmicVeto(event):
                self.Histos['{}/tktkdca_after_drcosmic'.format(chan)].Fill(lj.minTwoTrackDist(), aux['wgt'])

            absdz = []
            for dz in lj.pfcand_tkDz:
                self.Histos['{}/tkdz'.format(chan)].Fill(dz, aux['wgt'])
                absdz.append(abs(dz))
            self.Histos['{}/maxabstkdz'.format(chan)].Fill(max(absdz), aux['wgt'])
            if lj.passCosmicVeto(event):
                self.Histos['{}/maxabstkdz_after_drcosmic'.format(chan)].Fill(max(absdz), aux['wgt'])

            if passAllCosmicVeto and max(absdz)>40: passAllCosmicVeto=False

        if passAllCosmicVeto:
            self.Histos['{}/grandcosmicvetores'.format(chan)].Fill(1, aux['wgt'])


histCollection = [
    {
        'name': 'tktkdca',
        # 'binning': [[0,1,2,5,10,25,50,75,100]],
        'binning': (100,0,100),
        'title': 'Lepton-jet min track-track DCA;D.C.A [cm];counts',
    },
    {
        'name': 'tktkdca_after_drcosmic',
        # 'binning': [[0,1,2,5,10,25,50,75,100]],
        'binning': (100,0,100),
        'title': 'Lepton-jet min track-track DCA (#DeltaR_{cosmic}>0.05);D.C.A [cm];counts',
    },
    {
        'name': 'tkdz',
        'binning': (400,-200,200),
        'title': 'muon-type lepton-jet track dz;dz [cm];counts',
    },
    {
        'name': 'maxabstkdz',
        'binning': (400,0,200),
        'title': 'muon-type lepton-jet max track |dz|;|dz| [cm];counts',
    },
    {
        'name': 'maxabstkdz_after_drcosmic',
        'binning': (400,0,200),
        'title': 'muon-type lepton-jet max track |dz| (#DeltaR_{cosmic}>0.05);|dz| [cm];counts',
    },
    {
        'name': 'grandcosmicvetores',
        'binning': (2,0,2),
        'title': 'total cosmic veto result;;counts',
    },
]
