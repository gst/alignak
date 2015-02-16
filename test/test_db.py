#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2009-2014:
#    Gabes Jean, naparuba@gmail.com
#    Gerhard Lausser, Gerhard.Lausser@consol.de
#
# This file is part of Shinken.
#
# Shinken is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Shinken is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Shinken.  If not, see <http://www.gnu.org/licenses/>.

#
# This file is used to test reading and processing of config files
#

import sys

from shinken_test import ShinkenTest, unittest
from shinken.db import DB


class TestConfig(ShinkenTest):
    # setUp is inherited from ShinkenTest

    def create_db(self):
        self.db = DB(table_prefix='test_')

    def test_create_insert_query(self):
        self.create_db()
        data = {'id': "1", "is_master": True, 'plop': "master of the universe"}
        q = self.db.create_insert_query('instances', data)
        if sys.version_info < (3,):
            expected = "INSERT INTO test_instances  (is_master , id , plop  ) VALUES ('1' , '1' , 'master of the universe'  )"
            self.assertEqual(expected, q)
        else:
            expected = "zz" # "INSERT INTO test_instances  (plop , id , is_master  ) VALUES ('master of the universe' , '1' , '1'  )"
            expected = ["INSERT INTO test_instances  (id , plop , is_master  ) VALUES ('1' , 'master of the universe' , '1'  )",
                      "INSERT INTO test_instances  (id , is_master , plop  ) VALUES ('1' , '1' , 'master of the universe'  )",
                      "INSERT INTO test_instances  (is_master , id , plop  ) VALUES ('1' , '1' , 'master of the universe'  )",
                      "INSERT INTO test_instances  (plop , id , is_master  ) VALUES ('master of the universe' , '1' , '1'  )",
                      "INSERT INTO test_instances  (plop , is_master , id  ) VALUES ('master of the universe' , '1' , '1'  )",
                      "INSERT INTO test_instances  (is_master , id , plop  ) VALUES ('1' , '1' , 'master of the universe'  )",
                      "INSERT INTO test_instances  (is_master , plop , id  ) VALUES ('1' , 'master of the universe' , '1'  )"]
            self.assertIn(q, expected)


        # Now some UTF8 funny characters
        data = {'id': "1", "is_master": True, 'plop': '£°é§'}
        q = self.db.create_insert_query('instances', data)
        #print "Q", q
        c = "INSERT INTO test_instances  (is_master , id , plop  ) VALUES ('1' , '1' , '£°é§'  )"
        print(type(q), type(c))
        print(len(q), len(c))
        if sys.version_info < (3,):
            self.assertEqual(c, q)
        else:
            self.assertIn(q,
                          ["INSERT INTO test_instances  (id , plop , is_master  ) VALUES ('1' , '£°é§' , '1'  )",
                           "INSERT INTO test_instances  (plop , is_master , id  ) VALUES ('£°é§' , '1' , '1'  )",
                           "INSERT INTO test_instances  (is_master , plop , id  ) VALUES ('1' , '£°é§' , '1'  )",
                           "INSERT INTO test_instances  (is_master , id , plop  ) VALUES ('1' , '1' , '£°é§'  )",
                           "INSERT INTO test_instances  (plop , id , is_master  ) VALUES ('£°é§' , '1' , '1'  )",
                           "INSERT INTO test_instances  (id , is_master , plop  ) VALUES ('1' , '1' , '£°é§'  )"
                           ])

    def test_update_query(self):
        self.create_db()
        data = {'id': "1", "is_master": True, 'plop': "master of the universe"}
        where = {'id': "1", "is_master": True}
        q = self.db.create_update_query('instances', data, where)
        # beware of the last space
        print("Q", q)
        if sys.version_info < (3,):
            self.assertEqual("UPDATE test_instances set plop='master of the universe'  WHERE is_master='1' and id='1' ", q)
        else:
            self.assertIn(q,
                          ["UPDATE test_instances set plop='master of the universe'  WHERE id='1' and is_master='1' ",
                           "UPDATE test_instances set plop='master of the universe'  WHERE is_master='1' and id='1' "])

        # Now some UTF8 funny characters
        data = {'id': "1", "is_master": True, 'plop': '£°é§'}
        where = {'id': "£°é§", "is_master": True}
        q = self.db.create_update_query('instances', data, where)
        #print "Q", q
        c = "UPDATE test_instances set plop='£°é§'  WHERE is_master='1' and id='£°é§'"
        if sys.version_info < (3,):
            self.assertEqual(c.strip(), q.strip())
        else:
            self.assertIn(q, [
                "UPDATE test_instances set plop='£°é§'  WHERE id='£°é§' and is_master='1' ",
                "UPDATE test_instances set plop='£°é§'  WHERE is_master='1' and id='£°é§' "
            ])




if __name__ == '__main__':
    unittest.main()
