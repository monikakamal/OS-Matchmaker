function handleButtonClick(action) {
    switch(action) {
        case 'setup':
            alert("Step 1: Lite Setup starting! Please check the documentation.");
            break;
        case 'bugs':
            alert("Step 2: Searching for bugs! Opening the GitHub issues list...");
            break;
        case 'fix':
            alert("Step 3: Code Fix! Start applying changes in your editor.");
            break;
        case 'submit':
            alert("Step 4: Submit & Level Up! Generate a Pull Request.");
            break;
        default:
            alert("Button clicked!");
    }
}