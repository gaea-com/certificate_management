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



function collapse_ajax(selector, dn_company) {
    var url = "/cert/domain_classify/";
    msg = {
        "dns_company": dn_company
    };

    $.ajax({
        url: url,
        type: "GET",
        dataType: "json",
        data: msg,
        success: function (data) {
            $(selector + " div > .table tr:not(:first)").empty(); //清空table（除了第一行以外）

            if (JSON.stringify(data) === '{}' || JSON.stringify(data) === '[]') {
                // 没有查到一级域名时，设为None
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
                    + "</tr>";

                $(selector + " div > .table").append(trHTML);  //在table最后面添加一行
            }
            for (item in data) {
                var open_url = "/cert/dns_info/" + data[item]["domain"] + "/";
                var trHTML = "<tr>"
                    + "<td>"
                    + data[item]["domain"]
                    + "</td>"
                    + "<td>"
                    + "正常"
                    + "</td>"
                    + "<td>"
                    + "<a href=" + "\'" + open_url + "\'" + ">解析</a>"
                    + "</td>"
                    + "</tr>";

                $(selector + " div > .table").append(trHTML);  //在table最后面添加一行
            }
            // 去掉<a>标签下划线
            $("a").css("text-decoration", "none");
        },
        error: function (data, textStatus, errorThrown) {
            alert("domain archive " + "\n" + textStatus + "\n" + errorThrown);
        }
    })
}

$(function () {
    collapse_ajax("#collapse-1", "DnsPod")
});


function collapse_event(element) {
    var selector = $(element).attr("href");
    var dns_company = $(selector).parent().find("div h6 a").text();
    var dn_company = $.trim(dns_company);
    console.log(dn_company);

    setTimeout(function () {
        if ($(selector).hasClass("collapse show")) {
            console.log("delay exec");
            collapse_ajax(selector, dn_company)
        }
    }, 1000);
}


