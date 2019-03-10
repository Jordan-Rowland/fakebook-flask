let flash_close = document.querySelector('.close-flash');
let flash_msg = document.querySelector('.flash-msg');

if (flash_close) {
    flash_close.addEventListener('click', event => {
        flash_msg.classList.add('hide');
    });
}

