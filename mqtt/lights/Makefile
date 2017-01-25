
IP=172.17.3.250
LIB=../../lib/micropython/
REPL_PATH=../../../webrepl/

upload:
	$(REPL_PATH)webrepl_cli.py main.py $(IP):main.py
	$(REPL_PATH)webrepl_cli.py config.py $(IP):config.py

	
	$(REPL_PATH)webrepl_cli.py $(LIB)mock.py $(IP):mock.py
	$(REPL_PATH)webrepl_cli.py $(LIB)utils.py $(IP):utils.py
	$(REPL_PATH)webrepl_cli.py $(LIB)mqtt/simple.py $(IP):mqtt/simple.py
	$(REPL_PATH)webrepl_cli.py $(LIB)mqtt/items.py $(IP):mqtt/items.py
