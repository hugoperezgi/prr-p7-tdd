elo:
	zypper install -y python3
	code --install-extension ms-python.python
	zypper install -y strace
	zypper install -y tree
server:
	python3 srv.py &
killServer:
	python3 killsrv.py
	
client1:
	python3 cli.py 127.0.0.1 6868 127.0.0.1 6969 Fulanito
client2:
	python3 cli.py 127.0.0.1 7070 127.0.0.1 6969 Menganito

testServer:
	python3 srv_test.py
testClient:
	python3 cli_test.py
