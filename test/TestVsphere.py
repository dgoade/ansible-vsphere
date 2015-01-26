#!/usr/bin/env python

import traceback
import unittest
import os
import os.path
import re
#import yaml
import env
import sys

class TestVsphere(unittest.TestCase):

    ss_tree = [
        {
            'dynamicType': '<unset>',
            'dynamicProperty': [],
            'snapshot': 'vim.vm.Snapshot:snapshot-3591',
            'vm': 'vim.VirtualMachine:vm-3414',
            'name': 'preUpdates',
            'description': '',
            'id': 1,
            'createTime': '2015-01-08T15:20:51.385892Z',
            'state': 'poweredOn',
            'quiesced': False,
            'backupManifest': '<unset>',
            'childSnapshotList': [
            {
                'dynamicType': '<unset>',
                'dynamicProperty': [],
                'snapshot': 'vim.vm.Snapshot:snapshot-3744',
                'vm': 'vim.VirtualMachine:vm-3414',
                'name': 'WU_2015-01-14@16:33:38',
                'description': '',
                'id': 44,
                'createTime': '2015-01-14T21:33:40.21753Z',
                'state': 'poweredOff',
                'quiesced': False,
                'backupManifest': '<unset>',
                'childSnapshotList': [
                {
                    'dynamicType': '<unset>',
                    'dynamicProperty': [],
                    'snapshot': 'vim.vm.Snapshot:snapshot-3745',
                    'vm': 'vim.VirtualMachine:vm-3414',
                    'name': 'WU_2015-01-14@16:34:47',
                    'description': '',
                    'id': 45,
                    'createTime': '2015-01-14T21:34:49.827722Z',
                    'state': 'poweredOff',
                    'quiesced': False,
                    'backupManifest': '<unset>',
                    'childSnapshotList': [
                        {
                            'dynamicType': '<unset>',
                            'dynamicProperty': [],
                            'snapshot': 'vim.vm.Snapshot:snapshot-3780',
                            'vm': 'vim.VirtualMachine:vm-3414',
                            'name': 'WU_2015-01-16@13:07:05',
                            'description': '',
                            'id': 54,
                            'createTime': '2015-01-16T18:07:15.772036Z',
                            'state': 'poweredOff',
                            'quiesced': False,
                            'backupManifest': '<unset>',
                            'childSnapshotList': [],
                            'replaySupported': False
                         }
                      ],
                      'replaySupported': False
                   }
                ],
                'replaySupported': False
             },
            {
                'dynamicType': '<unset>',
                'dynamicProperty': [],
                'snapshot': 'vim.vm.Snapshot:snapshot-3749',
                'vm': 'vim.VirtualMachine:vm-3414',
                'name': 'WU_2015-01-14@16:33:38',
                'description': '',
                'id': 44,
                'createTime': '2015-01-14T21:33:40.21753Z',
                'state': 'poweredOff',
                'quiesced': False,
                'backupManifest': '<unset>',
                'childSnapshotList': []
            }
          ],
          'replaySupported': False
       }
    ]

    def test_num_snapshot_ancestors(self):

        ss = snapshot()

        rval = ss.num_snapshot_ancestors(self.ss_tree,
            'vim.vm.Snapshot:snapshot-3591')
        self.assertEqual(rval, 0)

        rval = ss.num_snapshot_ancestors(self.ss_tree,
            'vim.vm.Snapshot:snapshot-3744')
        self.assertEqual(rval, 1)

        rval = ss.num_snapshot_ancestors(self.ss_tree,
            'vim.vm.Snapshot:snapshot-3745')
        self.assertEqual(rval, 2)

        rval = ss.num_snapshot_ancestors(self.ss_tree,
             'vim.vm.Snapshot:snapshot-3780')
        self.assertEqual(rval, 3)

        rval = ss.num_snapshot_ancestors(self.ss_tree,
             'vim.vm.Snapshot:snapshot-3749')
        self.assertEqual(rval, 1)

    def test_snapshot_ancestor(self):

        ss = snapshot()

        rval = ss.snapshot_ancestor(self.ss_tree,
                                    'vim.vm.Snapshot:snapshot-3780', 1)
        self.assertEqual(rval, 'vim.vm.Snapshot:snapshot-3745')

        rval = ss.snapshot_ancestor(self.ss_tree,
                                    'vim.vm.Snapshot:snapshot-3780', 2)
        self.assertEqual(rval, 'vim.vm.Snapshot:snapshot-3744')


        rval = ss.snapshot_ancestor(self.ss_tree,
                                    'vim.vm.Snapshot:snapshot-3780', 3)
        self.assertEqual(rval, 'vim.vm.Snapshot:snapshot-3591')


        rval = ss.snapshot_ancestor(self.ss_tree,
                                    'vim.vm.Snapshot:snapshot-3780', 4)
        self.assertEqual(rval, None)

        rval = ss.snapshot_ancestor(self.ss_tree,
                                    'vim.vm.Snapshot:snapshot-3749', 1)
        self.assertEqual(rval, 'vim.vm.Snapshot:snapshot-3591')

    def test_ss_name_from_ss_prop(self):

        ss = snapshot()

        rval = ss.ss_name_from_ss_prop(self.ss_tree,
                                       'vim.vm.Snapshot:snapshot-3749')
        self.assertEqual(rval, 'WU_2015-01-14@16:33:38')

        rval = ss.ss_name_from_ss_prop(self.ss_tree,
                                       'vim.vm.Snapshot:snapshot-3591')
        self.assertEqual(rval, 'preUpdates')

class snapshot():

    def ss_name_from_ss_prop_lookup(self, tree, ss_prop):

        rval = None

        #if tree.snapshot == ss_prop:
        if tree['snapshot'] == ss_prop:
            rval = tree['name']
        else:
            #for child in tree.childSnapshotList:
            for child in tree['childSnapshotList']:
                rval = self.ss_name_from_ss_prop_lookup(child, ss_prop)
                if rval:
                    break

        return rval

    def ss_name_from_ss_prop(self, ss_list, ss_prop):

        rval = None

        try:
            for root_snap in ss_list:
                rval = self.ss_name_from_ss_prop_lookup(root_snap, ss_prop)
                if rval:
                    break
        except IndexError:
            rval = None

        return rval

    def count_snapshot_ancestors(self, tree, ss_name, ancestor_count):

        rval = ancestor_count
        found = False

        #if tree.snapshot == ss_name:
        if tree['snapshot'] == ss_name:
            rval = ancestor_count
            found = True
        else:
            #for child in tree.childSnapshotList:
            for child in tree['childSnapshotList']:
                found, rval = self.count_snapshot_ancestors(child, ss_name, rval)
                if found:
                    rval += 1
                    break

        return found, rval

    def num_snapshot_ancestors(self, ss_list, ss_name):

        try:
            found = False
            ancestor_count = 0
            for root_snap in ss_list:
                found, ancestor_count = self.count_snapshot_ancestors(root_snap, ss_name, 0)
                if found:
                    break
        except IndexError:
            ancestor_count = 0

        return ancestor_count

    def get_snapshot_ancestry(self, tree, ss_name, ancestry):

        rval = None
        found_descendant = False

        cur_ss_name = tree['snapshot']
        #cur_ssn_name = tree.snapshot
        if cur_ss_name == ss_name:
            found_descendant = True
            ancestry.append(cur_ss_name)
        else:
            #for child in tree.childSnapshotList:
            for child in tree['childSnapshotList']:
                ancestry.append(cur_ss_name)
                found_descendant, rval = self.get_snapshot_ancestry(child,
                                                                    ss_name,
                                                                    ancestry)
                if found_descendant:
                    break
                else:
                    ancestry.pop()

        return found_descendant, ancestry

    def snapshot_ancestor(self, ss_list, ss_name, gens_prior):

        ancestor_name = None

        try:
            found = False
            ancestor_count = self.num_snapshot_ancestors(ss_list, ss_name)
            if ancestor_count >= gens_prior:
                ancestry = []
                for root_snap in ss_list:
                    found, ancestry = self.get_snapshot_ancestry(
                        root_snap, ss_name, ancestry)
                    if found:
                        break
                if found:
                    gens = len(ancestry)
                    ancestor_name = ancestry[gens - (gens_prior + 1)]
        except IndexError:
            ancestor_count = 0

        return ancestor_name

if __name__ == '__main__':
    unittest.main()
