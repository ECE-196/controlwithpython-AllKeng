### How does the DevBoard handle received serial messages? How does this differ from the naïve approach?
* **The DevBoard triggers an interrupt upon receiving serial messages and then calls the on_event functions written. It reads the byte, checks to see if it is a valid state to update the LED state and then sends an OK byte. If not valid then it sends an ERR byte.**

* The naive approach is always checking the serial port for incoming messages (aka putting the on_event code inside the loop() function). Our DevBoard method is different by being event triggered or only taking action when receiving a new byte. 
    * **Our method is more efficient and responsive to received serial messages by not wasting resources to continuously check the port (polling)  and allowing the devboard to perform other actions in parallel.**

### What does `detached_callback` do? What would happen if it wasn't used?
* Detached_callback makes a function run in a separate thread (asynchronously). It separates the function from the main execution flow, allowing for parallelism. 
* If it were not used then the UI would freeze if the serial message takes too long or gets stuck. Essentially, whatever delay in sending would stop the UI and a user from doing anything. 

### What does `LockedSerial` do? Why is it _necessary_?
* LockedSerial prevents the race condition of multiple threads using the serial port at once. It makes it so only one thread could use the serial port at a time. Every operation / byte sent will happen one after the each. 
* It is necessary because we don't want to have corrupted data or undefined behavior due to trying to make changes on the same thing at the same time from multiple threads. It ensures a lock around the serial port so there will be serial, rather than parallel usage of it
