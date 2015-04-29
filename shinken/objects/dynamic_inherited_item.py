
from __future__ import unicode_literals, print_function


"""
POC for "dynamic" inherited shinken **_objects_** attributes.

This proof the feasibility to have dynamically inherited attributes.

Which permit to change a template attribute value and by the mean of the dynamic inheritance
 also have the new value directly in any of the objects which use the template ..

"""


class MyObjectsMetaClass(type):

    def __new__(mcs, name, bases, dct):
        print('Creating new class for %s ..' % name)
        cls = super(mcs, mcs).__new__(mcs, name, bases, dct)
        # '_by_name' dict maps the "template" name to
        # the template object, when there are some defined.
        cls._by_name = {}
        cls.use = []
        # 'use' is conveniently set on the class so to have a default value
        # so we don't have to do things like "if instance.use is not None"
        # or "getattr(instance, 'use', [])" ..
        cls.id = 1  # so to not have to assign it in all classes
        # other "Object" class (Host, etc..) level things can be done here
        # if needed..
        return cls

    # could be defined (as @classmethod) on Item itself !
    def _add_item(cls, item):
        prev = cls._by_name.setdefault(item.name, item)
        if prev != item:
            # we don't want that !
            raise RuntimeError('%s > duplicated object name !' % cls)


TODO = object()  # TODO, ToDefine or ToDeclare or ToDiscuss about ..


class Item(object):

    __metaclass__ = MyObjectsMetaClass

    properties = {
        'name':     TODO,  # not necessarily required here..
        'register': TODO,  # hmm.. could be the same.. or not.
    }

    def __init__(self, **kw):
        cls = self.__class__
        for k, v in kw.iteritems():
            if k == 'use':
                v = list(filter(lambda s: s, map(unicode.strip, v.split(','))))

            setattr(self, k, v)

            if k == 'name':
                # add this item in the '_by_name' dict attached to the class,
                # IF AND ONLY IF it has an explicit name attribute provided:
                cls._add_item(self)
                # NB: this could be done at an external level than here too !!

    def __getattr__(self, attr, *args):
        """
        Here comes the "magic" - for the not careful or usual reader :p -
        This is called if 'self' doesn't have the 'attr' attribute.
        """
        assert not args or 1 == len(args)
        if attr in self.properties:  # this is one-third of the magic !
            for u in self.use:  # this is 2-third !
                try:
                    p = self._by_name[u]
                except KeyError:
                    # damn we "use" something which doesn't exist.. :/
                    pass
                else:
                    try:
                        # this is the last part of the magic !!!
                        return getattr(p, attr)
                    except AttributeError:
                        pass
            if args:  # if there had a default provided, return it:
                return args[0]
            # otherwise :
            raise AttributeError('%s unavailable here nor in any of my "parent(s)" (use)' % attr)
        # we don't manage any other "dynamic" attribute (but we could), so :
        if args:
            return args[0]
        raise AttributeError('%s has no %r attribute' % (self, attr))

    @classmethod
    def make_template(cls, **kw):
        kw.update(require='0')
        return cls(**kw)


class SchedulingItem(Item):
    properties = Item.properties.copy()
    properties.update(
        check_command=TODO,
        check_period=TODO,
        max_check_attempts=TODO,
        check_interval=TODO,
        retry_interval=TODO,
        active_checks_enabled=TODO,
        passive_checks_enabled=TODO,
        # etc..
    )


class Host(SchedulingItem):
    properties = SchedulingItem.properties.copy()
    properties.update(
        address=TODO,
        host_name=TODO,
        # etc..
    )


class Service(SchedulingItem):
    properties = SchedulingItem.properties.copy()
    properties.update(
        host_name=TODO,
        service_description=TODO,
    )


#############################################################################

if __name__ == '__main__':

    print("Host.id", Host.id)
    print("Service.id", Service.id)

    host_tpl1 = Host.make_template(
        name='tpl1',
        active_checks_enabled='1', check_command='check-tcp')

    host_tpl2 = Host.make_template(name='tpl2', active_checks_enabled='0')

    svc_base_tpl = Service.make_template(
        name='base_tpl',
        active_checks_enabled='1', passive_checks_enabled='0',
        check_interval=5, retry_interval=3)

    svc_tpl1 = Service.make_template(
        name='tpl1', use='base_tpl',
        service_description='svc1', check_command='check-svc1')

    svc_tpl2 = Service.make_template(
        name='tpl2', use='base_tpl',
        service_description='svc2', check_command='check-svc2')

    svc_tpl3 = Service.make_template(
        name='tpl3', use='base_tpl',
        service_description='svc3', check_command='check-svc3')

    all_hosts = []
    all_services = []
    for addr in range(2, 10):
        host = Host(use=host_tpl1.name,
                    host_name='host%s' % addr, address='127.0.0.%s' % addr)
        all_hosts.append(host)

        for i in range(1, 4):
            tplX = 'tpl%s' % i
            svc = Service(use=tplX, host_name=host.host_name)
            all_services.append(svc)

    hst0 = all_hosts[0]
    print("currently %s has check_command = %s" % (hst0, hst0.check_command))
    print("now updating the base template (%s) check_command to 'changed!'" % (host_tpl1,))
    host_tpl1.check_command = 'changed!'
    print("and now %s check_command has : %s" % (hst0, hst0.check_command))

    print("==============================")

    svc = all_services[-1]
    print("currently %s has check_interval : %s" % (svc, svc.check_interval))
    print("now updating its template.. to 42")
    svc_tpl3.check_interval = 42
    print("and now %s has check_interval : %s" % (svc, svc.check_interval))
    print("now updating the check_interval on the service instance ..")
    svc.check_interval = 10
    print("and now %s has - ofcourse - check_interval : %s" % (svc, svc.check_interval))
    print("now re-updating on the template ..")
    svc_tpl3.check_interval = 50
    print("and deleting the attribute on the instance ..")
    del svc.check_interval
    print("and now %s has - ofcourse - check_interval : %s" % (svc, svc.check_interval))

