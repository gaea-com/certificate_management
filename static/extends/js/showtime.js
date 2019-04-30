function show_time() {
    //获得显示时间的div
    time_span = document.getElementById('showtime');
    var now = new Date();

    var week = now.getDay();
    var weekday;
    switch (week) {
        case 0:
            weekday = '星期日';
            break;
        case 1:
            weekday = '星期一';
            break;
        case 2:
            weekday = '星期二';
            break;
        case 3:
            weekday = '星期三';
            break;
        case 4:
            weekday = '星期四';
            break;
        case 5:
            weekday = '星期五';
            break;
        case 6:
            weekday = '星期六';
            break;
    }

    var year = now.getFullYear();
    var month = now.getMonth() + 1;
    var day = now.getDate();
    var hour = now.getHours();
    var minute = now.getMinutes();
    var second = now.getSeconds();

    if (month >= 1 && month <= 9) {
        month = "0" + month;
    }
    if (day >= 0 && day <= 9) {
        day = "0" + day;
    }

    //替换div内容
    time_span.innerHTML = year + "-" + month + "-" + day + " " + hour + ":" + minute + ":" + second + " " + weekday;
    //等待一秒钟后调用time方法，由于settimeout在time方法内，所以可以无限调用
    setTimeout(show_time, 1000);
}

show_time();