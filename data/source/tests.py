from ProcessManager import *
from StateManager import *

def fun1(caller, purpose):
	if purpose is "STOP_PURPOSE":
		print "fun1 stopping"
	elif purpose is "INIT_PURPOSE":
		print "fun1 starting"
	elif purpose is "FRAME_PURPOSE":
		print "fun1 processing"
	else:
		print "fun1 no purpose"

def fun2(caller, purpose):
	if purpose is "STOP_PURPOSE":
		print "fun2 stopping"
	elif purpose is "INIT_PURPOSE":
		print "fun2 starting"
	elif purpose is "FRAME_PURPOSE":
		print "fun2 processing"
	else:
		print "fun2 no purpose"

def fun3(caller, purpose):
	if purpose is "STOP_PURPOSE":
		print "fun3 stopping"
	elif purpose is "INIT_PURPOSE":
		print "fun3 starting"
	elif purpose is "FRAME_PURPOSE":
		print "fun3 processing"
	else:
		print "fun3 no purpose"
def test_process():
	proc_man = ProcessManager()
	print "  <process>"
	proc_man.process(None)
	
	print "  <create fun1>"
	id1 = proc_man.push(fun1, None)

	print "  <create fun2>"
	proc_man.push(fun2, None)
	
	print "  <process>"
	proc_man.process(None)
	
	print "  <kill fun1>"
	proc_man.pop(id1, None)

	print "  <create fun 3>"
	proc_man.push(fun3, None)
	
	print "  <process>"
	proc_man.process(None)

	print "  <kill all>"
	proc_man.pop_all(None)

	print "  <process>"
	proc_man.process(None)

def test_states():
	
	state_man = StateManager()

	print "  <process>"
        state_man.process(None)

        print "  <change to fun1>"
        id1 = state_man.push(fun1, None)

        print "  <change to fun2>"
        state_man.push(fun2, None)

        print "  <process>"
        state_man.process(None)

        print "  <kill fun2>"
        state_man.pop(None)

        print "  <change to fun 3>"
        state_man.push(fun3, None)

        print "  <process>"
        state_man.process(None)

        print "  <kill all>"
        state_man.pop_all(None)

        print "  <process>"
        state_man.process(None)
