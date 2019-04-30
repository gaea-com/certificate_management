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

function selectChange() {
    var domain_id = $("#selectDomain").val();
    var domain = $("#selectDomain").find("option:selected").text();

    if (domain_id == 0) {
        return false
    }
    var url = "/cert/view_cert/" + domain_id + "/";
    console.log(url);

    $.ajax({
        url: url,
        type: "GET",
        // dataType: "json",
        success: function (data) {
            var ret = (JSON.parse(data));

            if (ret["cert_content"]) {
                $("#certClipboard").text(ret["cert_content"]);
            } else {
                $("#certClipboard").text("None");
                $("#certClipboard").animate({height: "40px"});
            }

            if (ret["key_content"]) {
                $("#keyClipboard").text(ret["key_content"]);
            } else {
                $("#keyClipboard").text("None");
                $("#keyClipboard").animate({height: "40px"});
            }

            $("#domain").text(domain);

            // textarea的高度自适应
            $.each($("textarea"), function (i, n) {
                    $(n).css("height", n.scrollHeight + "px");
                }
            );
        },
        error: function (data, textStatus, errorThrown) {
            alert("cert page select Change " + textStatus + " : " + errorThrown);
        }
    });
}

function GetRequest() {
    // 获取跳转过来的页面中的 url 参数
    var url = location.search; //获取url中"?"符后的字串
    var theRequest = new Object();
    if (url.indexOf("?") != -1) {
        var str = url.substr(1);
        strs = str.split("&");
        for (var i = 0; i < strs.length; i++) {
            theRequest[strs[i].split("=")[0]] = decodeURIComponent(strs[i].split("=")[1]);
        }
    }
    return theRequest;
}

function download_cert(f_type) {
    // 下载证书和key
    var domain_id = $("#selectDomain").val();

    if (domain_id > 0) {
        var domain = $("#selectDomain").find("option:selected").text();
    } else {
        var getDomain = GetRequest();
        var domain = getDomain['domain'];
    }

    console.log("下载证书: " + domain);

    if (f_type === "cert") {
        if ($("#certClipboard").text() === "None" || !$("#certClipboard").text()) {
            return 1;
        }
        var url = '/cert/download_cert_file/' + domain;

    } else if (f_type === "key") {
        if ($("#keyClipboard").text() === "None" || !$("#keyClipboard").text()) {
            return 1;
        }
        var url = '/cert/download_key_file/' + domain;

    } else {
        alert("download file failed: 请选择域名");
        return 1;
    }
    window.location.href = url;
}


function load_cert_content() {
    // 加载证书和key内容
    var get_request = GetRequest();
    var id = get_request['id'];

    if (!id) {
        return false;
    }
    var domain = get_request["domain"];
    var url = '/cert/view_cert/' + id;

    $.ajax({
        url: url,
        type: "GET",
        success: function (data) {
            var ret = (JSON.parse(data));

            if (ret["cert_content"]) {
                $("#certClipboard").text(ret["cert_content"]);
            }

            if (ret["key_content"]) {
                $("#keyClipboard").text(ret["key_content"]);
            }

            $("#domain").text(domain);

            // textarea的高度自适应
            $.each($("textarea"), function (i, n) {
                $(n).css("height", n.scrollHeight + "px");
            });
        },
        error: function (data, textStatus, errorThrown) {
            alert("load cert content " + textStatus + " : " + errorThrown);
        }
    })
}

