#!/usr/bin/env python


from shinken.misc.regenerator import Regenerator
from shinken.brok import Brok

from shinken_test import ShinkenTest, unittest


class TestReversedList(ShinkenTest):
    def setUp(self):
        self.setup_with_file("etc/shinken_service_withhost_exclude.cfg")

    def test_reversed_list(self):
        """ Test to ensure new conf is properly merge with different servicegroup definition
        The first conf has all its servicegroup defined servicegroups.cfg and services.cfg
        The second conf has both, so that servicegroups defined ins services.cfg are genretaed by Shinken
        This lead to another generated id witch should be handled properly when regenerating reversed list / merging
        servicegroups definition
        """

        sg = self.sched.servicegroups.find_by_name('servicegroup_01')
        prev_id = sg.id

        reg = Regenerator()
        data = {"instance_id": 0}
        b = Brok('program_status', data)
        b.prepare()
        reg.manage_program_status_brok(b)
        reg.all_done_linking(0)


        self.setup_with_file("etc/shinken_reversed_list.cfg")

        reg.all_done_linking(0)

        #for service in self.sched.servicegroups:
        #    assert(service.servicegroup_name in self.sched.servicegroups.reversed_list.keys())
        #    assert(service.id == self.sched.servicegroups.reversed_list[service.servicegroup_name])

        sg = self.sched.servicegroups.find_by_name('servicegroup_01')
        assert(prev_id != sg.id)

        for sname in ['servicegroup_01', 'ok', 'flap', 'unknown', 'random',
                      'servicegroup_02', 'servicegroup_03', 'warning', 'critical',
                      'servicegroup_04', 'servicegroup_05', 'pending', 'mynewgroup']:
            sg = self.sched.servicegroups.find_by_name(sname)
            assert(sname is not None)



if __name__ == '__main__':
    unittest.main()
