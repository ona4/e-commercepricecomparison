function showNotification(message, duration = 10000) {
    const container = $('#notification-container');
    const notification = $('<div class="notification"></div>');
    const progress = $('<div class="notification-progress"></div>');
    
    notification.text(message);
    notification.append(progress);
    container.append(notification);

    setTimeout(() => {
        progress.css('width', '0');
    }, 100);

    setTimeout(() => {
        notification.css('top', '-100px');
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, duration);
}

$(document).ready(function() {
    const messages = $('.flashes li');
    if (messages.length > 0) {
        messages.each(function() {
            showNotification($(this).text());
        });
        $('.flashes').remove();
    }
});