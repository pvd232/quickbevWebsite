if you need to debug app after it has been closed (for example if you send a notification to the user while the app is closed) do the following 1. go to the current app file, select Product -> Scheme -> Edit Scheme, go to the "Run" tab, at the bottom of the options is a "Launch" button, changed from "Automatically" to "Wait for the executable to be launched" 2. print statements must be changed to "NSLog" 3. then to view the debug console select the "Window" tab in the Xcode toolbar -> Devices and Simulators -> when it opens select "Open console" and then make sure you filter for the message you are looking for by typing in the string value into the search bar and then pressing enter. then select the drop down that says "Any" and change it to "Message"

if you change something in react then when deploying app with gcloud app deploy you must run the following commands after cd into react-app directory
npm install react-dev-utils --save
npm run build
rm -r node_modules

gcloud commands
