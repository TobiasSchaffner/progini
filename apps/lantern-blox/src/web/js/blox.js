const maxX = $(window).width() - 100;
const maxY = $(window).height() - 100;

let creationDelay = 3000;
const timeDecrease = 50;
const doubleThreshold = creationDelay - (creationDelay / 3);
let boxCount = 0;
let userScore = 0;

$(document).ready(function () {
    creationLoop();
});

function creationLoop() {
    createRandomBox();
    if (creationDelay < doubleThreshold) {
        createRandomBox();
    }

    if (creationDelay > 0) {
        setTimeout(creationLoop, creationDelay);
        creationDelay = creationDelay - 50;
    } else {
        alert("You scored " + userScore + " points!");
    }
}

function createBox(x, y) {
    const template = $(".template.box").clone();
    const boxId = boxCount++;

    template.removeClass("template");
    template.css("top", y + "px");
    template.css("left", x + "px");
    template.attr("data-id", boxId);

    template.click(function (event) {
        const box = $(event.currentTarget);
        const id =box.attr("data-id");
        const timeoutId = box.attr("data-timeout-id");
        clickBox(id, timeoutId);
        box.unbind();
    });

    const timeoutId = setTimeout(function () {
        showVanishWarning(boxId);
    }, 1000);
    template.attr("data-timeout-id", timeoutId);

    $(".playground").append(template);
}

function createRandomBox() {
    let randomX = Math.floor(Math.random() * maxX);
    let randomY = Math.floor(Math.random() * maxY);

    createBox(randomX, randomY)
}

function showVanishWarning(id) {
    const box = $('.box[data-id=' + id + ']');
    box.addClass("vanishing");
    const timeoutId = setTimeout(function () {
        destroyBox(id)
    }, 1000);
    box.attr("data-timeout-id", timeoutId);
}

function destroyBox(id) {
    const box = $('.box[data-id=' + id + ']');
    box.off('click');
    box.removeClass("vanishing");
    box.removeClass("clicked");
    box.addClass("vanish");
    box.on('animationend', function (e) {
        box.remove();
    });
}

function clickBox(id) {
    const box = $('.box[data-id=' + id + ']');
    box.removeClass("vanishing");
    box.addClass("clicked");
    box.off('click');
    userScore++;
}
