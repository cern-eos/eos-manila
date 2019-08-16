"""Unit tests for the CERN EOS driver module."""

import os
import re
import socket
import mock
import ConfigParser

import ddt
from oslo_config import cfg

from manila import context
from manila import exception
import manila.share.configuration as config
from manila.share.drivers.eos_manila import driver
from manila.share import share_types
from manila import test
from manila.tests import fake_share
from manila import utils
from manila.share import api

class FakeResponse:
    def __init__(self):
        self.code = -1
        self.name = "fake_user"

CONF = cfg.CONF
configParser = ConfigParser.RawConfigParser()
BEGIN_PATH = os.path.expanduser('~') + "/eos_shares/"

@ddt.ddt
class EOSShareDriverTestCase(test.TestCase):
    """Tests EOSShareDriver."""

    def make_fake_share(self, name, proto="EOS"):
        fake_response = FakeResponse()
        share_location = BEGIN_PATH + fake_response.name + "/" + name
        return fake_share.fake_share(share_id="fake",
                                     display_name=name,
                                     display_description="fake",
                                     creator="fake_user",
                                     user_id="fake_id",
                                     share_proto=proto,
                                     size=1,
                                     metadata={'share_host': 'fake_location:/fake_share'},
                                     export_location=share_location)

    def setUp(self):
        super(EOSShareDriverTestCase, self).setUp()

        CONF.set_default('driver_handles_share_servers', False)

        self._execute = mock.Mock()
        self.fake_conf = config.Configuration(None)
        self._context = context.get_admin_context()
        self._share = self.make_fake_share('fake')
        self._driver = (
            driver.EosDriver(execute=self._execute,
                                configuration=self.fake_conf))
        self._driver.protocol_helper = mock.Mock()

    def test_get_share_stats_refresh_false(self):
        self._driver._stats = {'fake_key': 'fake_value'}
        result = self._driver.get_share_stats(False)
        self.assertEqual(self._driver._stats, result)

    @mock.patch('manila.share.driver.ShareDriver._update_share_stats')
    def test_update_share_stats(self, mock_super):
        self._driver.get_capacities = mock.Mock(return_value=[42, 23])
        self._driver._update_share_stats()

        mock_super.assert_called_once_with(
            dict(storage_protocol='EOS',
                 vendor_name='CERN',
                 share_backend_name='EOS',
                 driver_version='1.0',
                 total_capacity_gb=23,
                 free_capacity_gb=42,
                 reserved_percentage=5))

    @mock.patch('manila.share.api.API.get_share_metadata')
    def test_create_share(self, meta):
        #this mocks the host machine of the share
        meta.return_value = {'share_host': 'fake_location:/fake_share'}

        #this mocks the retrival of the current user logged in 
        self._driver.conn.identity.get_user = mock.Mock(return_value=FakeResponse())
        location = self._driver.create_share(self._context, self._share)

        #is the share on the correct host machine?
        self.assertEqual(self._share['metadata']['share_host'], 'fake_location:/fake_share')

        #is the share at the correct location on the host machine?
        self.assertEqual(self._share['export_location'], location)

        #does the share location actually exist?
        self.assertTrue(os.path.isdir(location))

        #is there a share.ini file at the location?
        self.assertTrue(os.path.isfile(location + "/share.ini"))

        #is the file correct?
        configParser.read(self._share["export_location"] + "/share.ini")
        self.assertEqual(configParser.get("MANILA-SHARE-CONFIG", "size"), "1")
        self.assertEqual(configParser.get("MANILA-SHARE-CONFIG", "managed"), "True")

        #clean up
        self._driver.delete_share(self._context, self._share) 

    @mock.patch('manila.share.api.API.get_share_metadata')
    def test_create_share_wrong_protocol(self, meta):
        wrong_proto_share = self.make_fake_share("fake_wrong_proto", "WRONG_PROTO")

        #this mocks the host machine of the share
        meta.return_value = {'share_host': 'fake_location:/fake_share'}

        #this mocks the retrival of the current user logged in
        self._driver.conn.identity.get_user = mock.Mock(return_value=FakeResponse())

        self.assertRaises(exception.EOSException,
                          self._driver.create_share,
                          self._context,
                          wrong_proto_share)


    @mock.patch('manila.share.api.API.get_share_metadata')
    def test_create_share_duplicate_name(self, meta):
        dup_share = self.make_fake_share("fake_duplicate")

        #this mocks the host machine of the share
        meta.return_value = {'share_host': 'fake_location:/fake_share'}

        #this mocks the retrival of the current user logged in
        self._driver.conn.identity.get_user = mock.Mock(return_value=FakeResponse())
           
        self._driver.create_share(self._context, dup_share)
        self.assertRaises(exception.EOSException,
                          self._driver.create_share,
                          self._context,
                          dup_share)
        #clean up
        self._driver.delete_share(self._context, dup_share)

    @mock.patch('manila.share.api.API.get_share_metadata')
    def test_delete_share(self, meta):
        delete_share = self.make_fake_share("delete_share")

        #this mocks the host machine of the share
        meta.return_value = {'share_host': 'fake_location:/fake_share'}

        #this mocks the retrival of the current user logged in
        self._driver.conn.identity.get_user = mock.Mock(return_value=FakeResponse())

        location = self._driver.create_share(self._context, delete_share)
        self._driver.delete_share(self._context, delete_share)

        self.assertFalse(os.path.isdir(location))

    @mock.patch('manila.share.api.API.get_share_metadata')
    def test_unmanage_share(self, meta):
        unmanage_share = self.make_fake_share("fake_unmanage")

        #this mocks the host machine of the share
        meta.return_value = {'share_host': 'fake_location:/fake_share'}

        #this mocks the retrival of the current user logged in
        self._driver.conn.identity.get_user = mock.Mock(return_value=FakeResponse())

        location = self._driver.create_share(self._context, unmanage_share)
        self._driver.unmanage(unmanage_share)

        configParser.read(unmanage_share["export_location"] + "/share.ini")
        self.assertEqual(configParser.get("MANILA-SHARE-CONFIG", "managed"), "False")

        self._driver.delete_share(self._context, unmanage_share)        
        
    @mock.patch('manila.share.api.API.get_share_metadata')
    def test_unmanage_share(self, meta):
        manage_share = self.make_fake_share("fake_manage")

        #this mocks the host machine of the share
        meta.return_value = {'share_host': 'fake_location:/fake_share'}

        #this mocks the retrival of the current user logged in
        self._driver.conn.identity.get_user = mock.Mock(return_value=FakeResponse())

        location = self._driver.create_share(self._context, manage_share)
        self._driver.unmanage(manage_share)
        self._driver.manage_existing(manage_share, {})

        configParser.read(manage_share["export_location"] + "/share.ini")
        self.assertEqual(configParser.get("MANILA-SHARE-CONFIG", "managed"), "True")

        self._driver.delete_share(self._context, manage_share)        

    @mock.patch('manila.share.api.API.get_share_metadata')
    def test_extend_share(self, meta):
        bigger_share = self.make_fake_share("fake_bigger")

        #this mocks the host machine of the share
        meta.return_value = {'share_host': 'fake_location:/fake_share'}

        #this mocks the retrival of the current user logged in
        self._driver.conn.identity.get_user = mock.Mock(return_value=FakeResponse())

        location = self._driver.create_share(self._context, bigger_share)
        self._driver.extend_share(bigger_share, 5)
        
        configParser.read(bigger_share["export_location"] + "/share.ini")
        self.assertEqual(configParser.get("MANILA-SHARE-CONFIG", "size"), "5")

        self._driver.delete_share(self._context, bigger_share)


    @mock.patch('manila.share.api.API.get_share_metadata')
    def test_shrink_share(self, meta):
        smaller_share = self.make_fake_share("fake_smaller")

        #this mocks the host machine of the share
        meta.return_value = {'share_host': 'fake_location:/fake_share'}

        #this mocks the retrival of the current user logged in
        self._driver.conn.identity.get_user = mock.Mock(return_value=FakeResponse())

        location = self._driver.create_share(self._context, smaller_share)
        self._driver.shrink_share(smaller_share, 0)

        configParser.read(smaller_share["export_location"] + "/share.ini")
        self.assertEqual(configParser.get("MANILA-SHARE-CONFIG", "size"), "0")

        self._driver.delete_share(self._context, smaller_share)
