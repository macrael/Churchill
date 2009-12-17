import threading

oneEvent = threading.Event()

class oneThread ( threading.Thread ):

    def run ( self ):

        print 'Thread One.'
        oneEvent.wait()
        print 'Executing One'

class twoThread ( threading.Thread ):

    def run ( self ):

        print 'Thread Two.'
        print 'Executing Two'

oneThread().start()
twoThread().start()
oneEvent.set()
