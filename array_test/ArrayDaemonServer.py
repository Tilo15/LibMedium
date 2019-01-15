from ArrayDaemon.Server import ArrayDaemonServerBase
import ArrayDaemon.Exceptions
import ArrayDaemon.Models

class ArrayDaemonServer(ArrayDaemonServerBase):
    
    def run(self):
        # This is called when the daemon is ready to communicate. Do your background tasks in here.
        # Communication is managed in a different thread, so feel free to place your infinate loop here.
        # A set of application connections can be found at 'self.applications'.
        # All your events are available to fire off at any time using 'self.event_name(*params)'.
        # To fire an event to a single application instance, pass in the application as the last
        # paramater in the event call, eg. 'self.event_name(param1, param2, application)'
        pass
    
    
    # Below are all the method calls you will need to handle.
    def new_list(self, items: list) -> ArrayDaemon.Models.ShoppingList:
        return ArrayDaemon.Models.ShoppingList("Pak'nSave", [ArrayDaemon.Models.ShoppingListItem(x, 1) for x in items])

    
    
    def get_list_items(self, list: ArrayDaemon.Models.ShoppingList) -> list:
        return list.items
    
    
    def get_lists_item_names(self, lists: list) -> list:
        arr = []
        for l in lists:
            arr += [x.item for x in l.items]

        return arr
    
    
    def get_2d_array(self, start: int) -> list:
        arr = []
        for i in range(start, 100):
            arr.append(range(start, 100))

        return arr
    
    
# If you run this module, it will run your daemon class above
if __name__ == '__main__':
    daemon = ArrayDaemonServer()

