from ArrayDaemon import ArrayDaemonConnection
import ArrayDaemon.Exceptions
import ArrayDaemon.Models

daemon = ArrayDaemonConnection()

daemon.tick.subscribe(lambda args: print("Ticked %i times" % args[0]))

slist = daemon.new_list(["bread", "milk", "cheese"])
print(slist.store)

print(daemon.get_list_items(slist))

print(daemon.get_2d_array(90))

slist2 = daemon.new_list(["butter", "chips", "ice cream"])

print(daemon.get_lists_item_names([slist, slist2]))


