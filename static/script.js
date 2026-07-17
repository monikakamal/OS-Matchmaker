console.log("Script file successfully loaded!");
function handleButtonClick(action) {
    switch(action) {
        case 'setup':
            // Yeh line alert ko hatakar naye page par le jayegi
            window.location.href = "/setup"; 
            break;
        case 'bugs':
            window.location.href = "/explore";
            break;
        case 'fix':
            window.location.href = "/fix";
            break;
        case 'submit':
            window.location.href = "/submit";
            break;
        default:
            console.log("Unknown action");
    }
}