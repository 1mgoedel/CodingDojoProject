const currentDateElement = document.getElementById('currentDate');
const todaysDate = new Date();
currentDateElement.textContent = todaysDate.toDateString();
