// 解决在使用js的ajax后，提交表单时出现Forbidden (CSRF token missing or incorrect.)问题
$(function () {
    $.ajaxSetup({
        headers: {"X-CSRFToken": getCookie("csrftoken")}
    });
});

// getCookie函数
function getCookie(name) {
    var arr, reg = new RegExp("(^| )" + name + "=([^;]*)(;|$)");

    if (arr = document.cookie.match(reg))
        return unescape(arr[2]);
    else
        return null;
}


function formatDate(d) {
    // 将指定的日期格式化为本地时间: 年/月/日
    var oldTime = (new Date(d)).getTime();
    var newTime = new Date(oldTime).toLocaleDateString();

    return newTime
}


function diffDays(endTime) {
    // 当前时间和过期时间相差天数
    var dateStart = new Date();
    var dateEnd = new Date(endTime);
    var difValue = (dateEnd - dateStart) / (1000 * 60 * 60 * 24);

    console.log(difValue);
    return Math.floor(difValue)
}


function selectSubDomainPage() {
    var domain_id = $("#selectSubDomain").val();
    var domain = $("#selectSubDomain").find("option:selected").text();
    // var url = "/cert/get_sub_domains/" + domain_id + "/";
    var url = "/cert/sub_domain_page";

    $(".page-description").text("域名: " + domain);

    var msg = {
        "domain_id": domain_id,
    };


    if (domain_id === "None" || domain_id === "0") {
        return false
    }

    $.ajax({
        url: url,
        type: "POST",
        dataType: "json",
        data: msg,
        success: function (data) {
            $("#sortable-table-1 tr:not(:first)").empty(); //清空table（除了第一行以外）

            if (JSON.stringify(data) === '{}') {
                // 当查询的域名没有子域名时，设为None
                var trHTML = "<tr>"
                    + "<td>"
                    + "None"
                    + "</td>"
                    + "<td>"
                    + "None"
                    + "</td>"
                    + "<td>"
                    + "None"
                    + "</td>"
                    + "<td>"
                    + "None"
                    + "</td>"
                    + "<td>"
                    + "None"
                    + "</td>"
                    + "<td>"
                    + "None"
                    + "</td>"
                    + "<td>"
                    + "None"
                    + "</td>"
                    + "</tr>";

                $("#sortable-table-1").append(trHTML);  //在table最后面添加一行
            }

            for (item in data) {
                console.log(data[item]["start_time"]);
                var start_time = data[item]["start_time"] ? formatDate(data[item]['start_time']) : "None";
                var end_time = data[item]["end_time"] ? formatDate(data[item]['end_time']) : "None";

                var remaining_time = data[item]["end_time"] ? diffDays(data[item]['end_time']) + " 天" : "None";

                var trHTML = "<tr>"
                    + "<td>"
                    + data[item]["protocol"]
                    + "</td>"
                    + "<td>"
                    + data[item]['sub_domain']
                    + "</td>"
                    + "<td>"
                    + data[item]['record_type']
                    + "</td>"
                    + "<td>"
                    + data[item]['record_value']
                    + "</td>"
                    + "<td>"
                    + start_time
                    + "</td>"
                    + "<td>"
                    + end_time
                    + "</td>"
                    + "<td>"
                    + remaining_time
                    + "</td>"
                    + "</tr>";

                $("#sortable-table-1").append(trHTML);  //在table最后面添加一行
            }
        },
        error: function (data, textStatus, errorThrown) {
            alert("sub domain page select " + "\n" + textStatus + "\n" + errorThrown);
        }
    });
}