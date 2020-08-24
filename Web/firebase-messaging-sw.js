importScripts('https://www.gstatic.com/firebasejs/4.8.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/4.8.1/firebase-messaging.js');

// Initialize Firebase
var config = {
    apiKey: "AIzaSyBu16EtBs7PrWwqhdcDIYhMGuq6RE_STek",
    authDomain: "eswcontest-smartthings.firebaseapp.com",
    databaseURL: "https://eswcontest-smartthings.firebaseio.com",
    projectId: "eswcontest-smartthings",
    storageBucket: "eswcontest-smartthings.appspot.com",
    messagingSenderId: "706465862197",
    appId: "1:706465862197:web:96d8ef7915bce48306577c",
    measurementId: "G-WV0MTWV5QK"
};
firebase.initializeApp(config);

const messaging = firebase.messaging();
messaging.setBackgroundMessageHandler(function (payload) {

    const title = "Messaging Test";
    const options = {
        body: payload.data.status
    };

    return self.registration.showNotification(title, options);
});
