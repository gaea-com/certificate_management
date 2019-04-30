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

function run_waitMe(text) {
    $('body').waitMe({
        effect: 'win8_linear',
        text: text,
        bg: 'rgba(255,255,255,0.7)',
        color: '#000',
        sizeW: '',
        sizeH: '',
    });
}

function add_css() {
    var c = {
        "cursor": "hand",
        "color": "#343a40",
        "opacity": "0.4",
    };
    return c
}

function add_attr() {
    var attrs = {
        "href": "javascript:void(0)",
        "disabled": "true",
    };
    return attrs
}

// 页面加载完成之后需要执行的代码
$(modify_row_style());

function modify_row_style() {
    $(".status").each(function () {
        var status = $(this).text();

        console.log("check status: " + status);

        if (status === "失败") {
            $(this).css("color", "red");
            $(this).parent().find('td button:first').attr('disabled', 'disabled');   // 将 index页面中 view 按钮禁用
            $(this).parent().find('td div div > a:nth-child(1), a:nth-child(2), a:nth-child(5)').css(
                add_css()
            );
            $(this).parent().find('td div div > a:nth-child(1), a:nth-child(2), a:nth-child(5)').attr(
                add_attr()
            );
            $(this).parent().find('td div div > a:nth-child(1), a:nth-child(2), a:nth-child(5)').removeAttr("onclick")

        } else if (status === "有效") {
            $(this).css("color", "#16A085");

        } else if (status === "创建中") {
            $(this).css("color", "#F4A460");
            $(this).parent().find('td button:first').attr('disabled', 'disabled');   // 将 index页面中 view 按钮禁用
            $(this).parent().find("td div div > a:nth-child(1), a:nth-child(2), a:nth-child(5)").css(
                add_css()
            );
            $(this).parent().find("td div div > a:nth-child(1), a:nth-child(2), a:nth-child(5)").attr(
                add_attr()
            );
            $(this).parent().find("td div div > a:nth-child(1), a:nth-child(2), a:nth-child(5)").removeAttr("onclick")

        } else if (status === "无效") {
            $(this).css("color", "#F4A460");
            $(this).parent().find("td div div > a:nth-child(1)").css(
                add_css()
            );
            $(this).parent().find("td div div > a:nth-child(1)").attr(
                add_attr()
            );
            $(this).parent().find("td div div > a:nth-child(1)").removeAttr("onclick");
            $(this).parent().find("td div div > a:nth-child(2)").text("启动");
            // $(this).parent().find("td div div > a:nth-child(2)").hover(
            //     function () {
            //         $(this).css("color", "#0056AF");
            //         $(this).css("text-decoration", "none");
            //     },
            //     function () {
            //         $(this).css("color", "#16A085")
            //     }
            // );

        } else {
            $(this).css("color", "#F4A460");
        }
    })
}


function create_ssl_ajax(messages) {
    var url = "/cert/create_cert_page";

    if (messages["cc_email"]) {
        var to_email = " , " + messages["cc_email"]
    } else {
        var to_email = "";
    }

    $.ajax({
        url: url,
        type: "POST",
        dataType: "json",
        data: messages,
        success: function (data) {
            // 隐藏wait效果
            $('body').waitMe('hide');

            if (JSON.stringify(data) === '{}') {
                swal({
                    title: "创建失败",
                    text: "服务器端异常，请检查",
                    icon: "error",
                    button: true
                })
            }

            if (data["status"] === "success") {
                swal({
                    title: "证书创建中",
                    text: data["message"],
                    icon: "success",
                    button: true
                })
                    .then((value) => {
                        // 清空 input 里的内容d
                        $("form fieldset input").val("")
                    });
            } else {
                swal({
                    title: "证书创建失败",
                    text: data["message"],
                    icon: "error",
                    button: true
                });
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            $('body').waitMe('hide');
            alert("添加证书 " + textStatus + " : " + errorThrown);
        }
    });
}


// 添加域名，创建证书
function create_ssl_cert() {
    var domain = $("#domain").val();
    var dns_company = $("#sel option:selected").val();
    var to_email = $("#to_email").val();
    var cc_email = $("#cc_email").val();

    var account_input = dns_company.toLowerCase();
    var api_1 = $("#" + account_input + "_key").val();
    var api_2 = $("#" + account_input + "_token").val();

    if (!domain || !to_email) {
        toastr.error('输入框中不能为空', 'Error', {positionClass: 'toast-top-right'});
        return false;
    }

    if (dns_company === "0") {
        toastr.error('请选择DNS解析商', 'Error', {positionClass: 'toast-top-right'});
        return false;
    }

    if (!api_1 || !api_2) {
        toastr.error('输入框中不能为空', 'Error', {positionClass: 'toast-top-right'});
        return false;
    }

    run_waitMe("Please wait...");

    var messages = {
        "domain": domain,
        "dns_company": dns_company,
        "api_1": api_1,
        "api_2": api_2,
        "to_email": to_email,
        "cc_email": cc_email,
    };

    create_ssl_ajax(messages);

    // 10后，开始向服务器端获取新增域名对应的状态，并将其状态更新在页面上。
    // setTimeout(function () {
    //     check_domain_status();
    // }, 10000);
}


function getNowFormatDate() {
    // 获取当前时间，格式YYYY-MM-DD
    var date = new Date();
    var seperator1 = "-";
    var year = date.getFullYear();
    var month = date.getMonth() + 1;
    var strDate = date.getDate();
    if (month >= 1 && month <= 9) {
        month = "0" + month;
    }
    if (strDate >= 0 && strDate <= 9) {
        strDate = "0" + strDate;
    }
    var currentdate = year + seperator1 + month + seperator1 + strDate;
    return currentdate;
}


function AddDays(dayIn) {
    // 对当前日期加n天
    var date = new Date();
    var myDate = new Date(date.getTime() + dayIn * 24 * 60 * 60 * 1000);
    var year = myDate.getFullYear();
    var month = myDate.getMonth() + 1;
    var day = myDate.getDate();
    CurrentDate = year + "-";
    if (month >= 10) {
        CurrentDate = CurrentDate + month + "-";
    } else {
        CurrentDate = CurrentDate + "0" + month + "-";
    }
    if (day >= 10) {
        CurrentDate = CurrentDate + day;
    } else {
        CurrentDate = CurrentDate + "0" + day;
    }
    return CurrentDate;
}


// 更新证书
function updateSSLCert(idx, id, domain) {
    var operateLabel = '#operate_' + idx;
    var startTimeLabel = $(operateLabel).parent().find('td:nth-child(3)');
    var expiredTimeLabel = $(operateLabel).parent().find('td:nth-child(4)');

    var expired_time = expiredTimeLabel.text();
    var end_time = new Date(expired_time);
    var now_time = new Date();
    var days = parseInt((end_time - now_time) / (1000 * 60 * 60 * 24));

    console.log("剩余天数: " + days);

    if (days > 29) {
        swal({
            text: "请在距离过期时间小于30天时再更新",
            icon: "warning",
            button: true
        });
        return 1;
    }

    run_waitMe("Please wait...");

    var URL = "/cert/update_ssl_cert/" + id + "/";
    $.ajax({
        url: URL,
        type: "POST",
        dataType: "json",
        // data: MSG,
        success: function (data) {
            $('body').waitMe('hide');

            console.log(typeof data);
            console.log(data);

            if (data["status"] === "success") {
                swal({
                    text: domain + " 域名证书正在更新",
                    icon: "success",
                    button: true
                })
                    .then((value) => {
                        startTimeLabel.text(getNowFormatDate());
                        expiredTimeLabel.text(AddDays(90))
                    });
            } else {
                swal({
                    title: "更新失败",
                    text: data["message"],
                    icon: "error",
                    button: true
                })
                    .then((value) => {
                        // 局部刷新
                        // $(".wrapper").load(location.href + ' .wrapper>*');
                        console.log("更新域名失败")
                    });
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            $('body').waitMe('hide');
            alert("更新证书 " + textStatus + " : " + errorThrown);
        }
    });
}


// 停用证书
function disableSSLCert(idx, id, domain) {
    console.log("stop domain id: " + id);
    console.log("stop domain: " + domain);

    run_waitMe("Please wait...");

    var URL = "/cert/disable_ssl_cert/" + id + "/";

    var _getOperateDone = function (type) {
        // 1 : true, 启用状态
        // 0 : false, 停用的状态
        var operateLabel = '#operate_' + idx;
        var stopLabel = '#operate_' + idx + ' a:nth-child(2)';
        var status = (type) ? '有效' : '无效';

        $(stopLabel).text((type) ? '停用' : '启用');
        $(operateLabel).parent().find('td.status').text(status);

        var updateLabel = '#operate_' + idx + ' a:nth-child(1)';

        if (type) {
            console.log("type: " + type);

            $(updateLabel).removeAttr("style disabled");
            $(operateLabel).parent().find('td.status').css("color", "#16A085");  // 有效时，将 status 颜色改为绿色 // 有效时，将 status 颜色改为绿色

            var fun = "updateSSLCert(" + idx + ", " + id + ", " + "\"" + domain + "\"" + ")";
            $(updateLabel).attr("onclick", fun);

        } else {
            $(operateLabel).parent().find('td.status').css("color", "#F4A460");  // 无效时，将 status 颜色改为橙色
            console.log("type: " + type + " 停用");

            $(updateLabel).removeAttr("onclick");
            $(updateLabel).css(add_css());
            $(updateLabel).attr("disabled");
        }
    };

    $.ajax({
        url: URL,
        type: "POST",
        success: function (data) {
            $('body').waitMe('hide');

            if (data === "invalid") {
                swal({
                    text: domain + " 证书已停用",
                    icon: "success",
                    button: true
                }).then((value) => {
                    _getOperateDone(0);
                });
            } else if (data === "valid") {
                swal({
                    text: domain + " 证书已启用",
                    icon: "success",
                    button: true
                }).then((value) => {
                    _getOperateDone(1);
                });
            } else {
                alert(data);
            }
        },
        error: function (data, textStatus, errorThrown) {
            $('body').waitMe('hide');
            alert("停用/启用证书 " + textStatus + " : " + errorThrown);
        }
    });
}


// 删除证书
function domainDelete(id, domain) {
    var URL = "/cert/delete_domain/" + id + "/";

    swal({
        title: "Are you sure?",
        text: "删除 " + domain + " ?",
        buttons: true,
        dangerMode: true,
    })
        .then((willDelete) => {
            if (willDelete) {
                run_waitMe("Please wait...");
                $.ajax({
                    url: URL,
                    type: "POST",
                    // dataType: "json",
                    success: function (data) {
                        $('body').waitMe('hide');
                        if (data === "delete_success") {
                            swal({
                                text: domain + " 已删除",
                                icon: "success",
                                button: true
                            })
                                .then((value) => {
                                    // 重载页面
                                    location.reload(true);
                                });
                        } else {
                            swal({
                                text: data,
                                icon: "error",
                                button: true
                            });
                        }
                    },
                    error: function (data, textStatus, errorThrown) {
                        $('body').waitMe('hide');
                        alert("删除证书 " + textStatus + " : " + errorThrown);
                    }
                });
            }
        });
}


function view_email(id) {
    $("#email_hidden_id").val(id);
    $('#baseModal').modal('show');
    var url = "/cert/view_email/" + id;

    $.get(url, function (data) {
        var data = $.parseJSON(data);
        var to_email = data["to_email"];
        var cc_email = data["cc_email"];

        console.log("to_email: " + to_email);
        console.log("cc_email: " + cc_email);

        $("#toEmail").val(to_email);

        if (cc_email) {
            $("#ccEmail").val(cc_email);

        } else {
            // $("#cc_email").val("没有设置抄送邮箱");
            $("#ccEmail").val("");
            $("#ccEmail").attr("placeholder", "None");
        }
    });
}

function modify_email() {
    var id = $("#email_hidden_id").val();
    $('#baseModal').modal('hide');

    var new_cc_email = $("#ccEmail").val();
    if (!new_cc_email) {
        return true;
    }

    var url = "/cert/modify_email/";
    var msg = {
        "id": id,
        "new_cc_email": new_cc_email,
    };
    $.post(url, msg, function (data) {
        console.log("email callback: ", data);
        if (data === "save_success") {
            toastr.success('抄送邮箱已更新', 'Success', {positionClass: 'toast-top-right'});

            $("#ccEmail").val("")
        } else {
            toastr.error(data, 'Error', {positionClass: 'toast-top-right'});
        }
    })
}


function view_cert(id, domain) {
    // index 页面 view 按钮跳转到证书页面
    // 跳转到新页面 并传参

    // var win = window.open("/cert/cert_page?id=" + id + "&" + "domain=" + domain, "_blank");
    var win = window.open("_blank");
    win.location = "/cert/cert_page?id=" + id + "&" + "domain=" + domain;
    // if (win == null) {
    //     alert('新窗口被弹出窗口拦截程序所阻挡。建议您将本站点加入到拦截程序设定的允许弹出名单中。有些弹出窗口拦截程序允许在长按Ctrl键时可以打开新窗口。');
    // }
    // window.open("/cert/cert_page?id=" + id + "&" + "domain=" + domain, "_blank");
}


function dns_info(domain) {
    // 跳转到新页面 并传参
    console.log("ddddd: " + domain);
    var win = window.open("_blank");
    win.location = "/cert/dns_info/" + domain + "/";
}


// 向服务器获取域名对应的状态，当前端和后端状态不一致时，以后端为准，并修改前端状态
function check_domain_status() {
    var url = "/cert/check_domain_status/";
    // console.log(url);

    $(".status").each(function () {
        var status = $(this).text();

        if (status === "创建中") {
            var that = this;
            var timer = setInterval(function () {
                console.log("start timer ==> %d", timer);

                var idx = $(that).parent().find('td:first').text();      // 序号
                var domain = $(that).parent().find('td:nth-child(2)').text();      // 域名

                var message = {
                    "domain": domain,
                };

                var operateCertLabel = '#operate_' + idx + ' button:nth-child(1)';     // 操作中的 View 按钮
                var operateUpdateLabel = '#operate_' + idx + ' div div a:nth-child(1)';     // 操作中的 更新 按钮
                var operateStopLabel = '#operate_' + idx + ' div div a:nth-child(2)';     // 操作中的 停用 按钮
                var operateEmailLabel = '#operate_' + idx + ' div div a:nth-child(5)';     // 操作中的 删除 按钮

                // var operateCertLabel = '#operate_' + idx + " button:contains('View')";     // 操作中的 View 按钮
                // var operateUpdateLabel = '#operate_' + idx + ' div div a:contains("更新")';     // 操作中的 更新 按钮
                // var operateStopLabel = '#operate_' + idx + ' div div a:contains("停用")';     // 操作中的 停用 按钮
                // var operateEmailLabel = '#operate_' + idx + ' div div a:contains("Email")';     // 操作中的 删除 按钮

                $.get(url, message, function (data) {
                    server_ret = JSON.parse(data);      // 将json类型转化为字典
                    console.log(server_ret);

                    var id = server_ret['id'];
                    var domain_status = server_ret['status'];

                    if (domain_status === "failed") {
                        $('#status_' + idx).text("失败");
                        $('#status_' + idx).css("color", "red");

                        $(operateUpdateLabel).removeAttr("onclick");
                        $(operateUpdateLabel).css(add_css());
                        $(operateUpdateLabel).attr(add_attr());

                        $(operateStopLabel).removeAttr("onclick");
                        $(operateStopLabel).css(add_css());
                        $(operateStopLabel).attr(add_attr());

                        $(operateCertLabel).removeAttr("onclick");
                        $(operateCertLabel).css(add_css());
                        $(operateCertLabel).attr(add_attr());

                        $(operateEmailLabel).removeAttr("onclick");
                        $(operateEmailLabel).css(add_css());
                        $(operateEmailLabel).attr(add_attr());

                        console.log("server status failed");
                        clearInterval(timer);
                        console.log('end timer ==> %d', timer);

                        toastr.error(domain + ": 证书创建失败", 'Error', {positionClass: 'toast-top-right'});

                    } else if (domain_status === "valid") {
                        $('#status_' + idx).text("有效");
                        $('#status_' + idx).css("color", "#16A085");

                        $(operateCertLabel).removeAttr("disabled");

                        $(operateUpdateLabel).removeAttr("style disabled");
                        var fun = "updateSSLCert(" + idx + ", " + id + ", " + "\"" + domain + "\"" + ")";
                        $(operateUpdateLabel).attr("onclick", fun);

                        $(operateStopLabel).removeAttr("style disabled");
                        var fun = "disableSSLCert(" + idx + ", " + id + ", " + "\"" + domain + "\"" + ")";
                        $(operateStopLabel).attr("onclick", fun);

                        $("#operateEmailLabel").removeAttr("style disabled");
                        // view_email('{{ item.id }}'); return false
                        var fun = "view_email(" + id + "); return false";
                        $(operateEmailLabel).attr("onclick", fun);

                        console.log("server status valid");
                        clearInterval(timer);
                        console.log('end timer ==> %d', timer);

                        toastr.success(domain + ': 证书创建成功', 'Success', {positionClass: 'toast-top-right'});

                    } else if (domain_status === "invalid") {
                        $('#status_' + idx).text("无效");
                        $('#status_' + idx).css("color", "#F4A460");

                        $(operateUpdateLabel).removeAttr("onclick");
                        $(operateUpdateLabel).css(add_css());
                        $(operateUpdateLabel).css(add_attr());

                        $(operateStopLabel).text("启动");
                        console.log("server status invalid");
                        clearInterval(timer);
                        console.log('end timer ==> %d', timer);

                    } else {
                        console.log(domain + " : " +  data);
                    }
                });
            }, 20000);
        }
    })
}


// 判断页面第一次加载还是刷新操作
// 页面刷新后 check_domain_status 函数中的定时器会失效，当页面被刷新时，再启动定时器
if (!window.name) {
    console.log("第一次打开页面 " + window.name);
    window.name = 'refresh_page';

} else {
    console.log("刷新页面后: " + window.name);
    setTimeout(function () {
        check_domain_status();
    }, 10000);
}


//上传文件的大小以及文件格式验证
// function check_file_format_size(obj) {
//     fileExt = obj.value.substr(obj.value.lastIndexOf(".")).toLowerCase();  //获得文件后缀名
//     console.log("文件格式: " + fileExt);
//
//     if (fileExt !== '.txt' && fileExt !== '.csv') {
//         swal({
//             text: "仅限于上传txt, csv格式文件",
//             icon: "error",
//             button: true
//         });
//         return false;
//     }
//     var fileSize = 0;
//     var isIE = /msie/i.test(navigator.userAgent) && !window.opera;
//     if (isIE && !obj.files) {
//         var filePath = obj.value;
//         var fileSystem = new ActiveXObject("Scripting.FileSystemObject");
//         var file = fileSystem.GetFile(filePath);
//         fileSize = file.Size;
//     } else {
//         fileSize = obj.files[0].size;
//     }
//
//     fileSize = Math.round(fileSize / 1024 * 100) / 100; //单位为KB
//     console.log("文件大小: " + fileSize);
//
//     if (fileSize >= 2048 || fileSize <= 0) {
//         swal({
//             text: "不能上传空文件且文件大小不能超过2M",
//             icon: "error",
//             button: true
//         });
//         return false;
//     }
// }


// function upload_files() {
//     // 隐藏模态框
//     $("#batchImportDomainModal").modal("hide");
//
//     var form_data = new FormData();
//     var len = $('#upload_file')[0].files.length;
//
//     console.log($('#upload_file')[0].files);
//     console.log(len);
//
//     for (var i = 0; i < len; i++) {
//         var file_info = $('#upload_file')[0].files[i];
//         console.log("file_info: " + file_info);
//
//         form_data.append('upload_domain_file', file_info);
//     }
//
//     var isChecked = $('#check_batch_hosting').prop('checked');
//     console.log("批量托管复选框: " + isChecked);
//     if (isChecked) {
//         form_data.append("isChecked", isChecked);
//     }
//
//     $.ajax({
//         url: '/cert/upload_files/',         // 这里对应url.py中的 url(r'upload_files', views.upload_files)
//         type: 'POST',
//         data: form_data,
//         processData: false,                 // tell jquery not to process the data
//         contentType: false,                 // tell jquery not to set contentType
//
//         success: function (data) {
//             swal({
//                 text: data,
//                 icon: "success",
//                 button: true,
//             })
//                 .then((value) => {
//                     // 文件上传成功后 清空文件上传控件的值
//                     // 浏览器的安全机制规定不可以直接用js修改file的value为有效值
//                     // 解决方法是设置file的value为空字符，或者把file的html重新初始化来解决清空的问题
//                     var uploaded_file = document.getElementById('upload_file');
//                     uploaded_file.outerHTML = uploaded_file.outerHTML;            //重新初始化了file的html
//                 });
//         }
//     });
// }


// function max_length(l) {
//     // l 为 list类型
//     var n = 0;
//     l.filter(function (item) {
//         n = Math.max(n, item.length);
//         return n;
//     });
//
//     console.log("max_length: " + n);
//     return n;
// }


// function query_sub_domain(id, domain) {
//
//     console.log("查询 " + domain + " 子域名");
//
//     $("#sub-domain-modal-title").text(domain + " 子域名");
//
//     $.ajax({
//         url: "/cert/query_sub_domain/" + id,
//         type: "GET",
//         dataType: "json",
//         // data: message,
//         success: function (data) {
//             $('body').waitMe('hide');
//             console.log("http: " + data["http"]);
//             console.log("https: " + data["https"]);
//
//             http_list_length = max_length(data["http"]);
//             https_list_length = max_length(data["https"]);
//             if (http_list_length > https_list_length) {
//                 max_l = http_list_length;
//             } else {
//                 max_l = https_list_length;
//             }
//
//             if (max_l >= 55) {
//                 $("#subDomainModal").children(".modal-dialog").addClass("modal-lg");
//             } else {
//                 $("#subDomainModal").children(".modal-dialog").removeClass("modal-lg");
//             }
//
//             var http = "";
//             for (var i = 0; i < data["http"].length; i++) {
//                 var http = "&nbsp;&nbsp;&nbsp;&nbsp;" + data["http"][i] + "<br>" + http;
//             }
//
//             var https = "";
//             for (var i = 0; i < data["https"].length; i++) {
//                 var https = "&nbsp;&nbsp;&nbsp;&nbsp;" + data["https"][i] + "<br>" + https;
//             }
//
//             $('#http-sub-domain').removeAttr("style");
//             $('#https-sub-domain').removeAttr("style");
//
//             $("#http-sub-domain").html("http: <br>" + http + "<br>");
//             $("#https-sub-domain").html("https: <br>" + https);
//
//             if (data["http"].length === 0) {
//                 $("#http-sub-domain").html("http: <br>" + "&nbsp;&nbsp;&nbsp;&nbsp;no http sub domain" + "<br>");
//                 $("#http-sub-domain").css("color", "red");
//             }
//
//             if (data["https"].length === 0) {
//                 $("#https-sub-domain").html("https: <br>" + "&nbsp;&nbsp;&nbsp;&nbsp;no https sub domain");
//                 $("#https-sub-domain").css("color", "red");
//             }
//
//             $("#subDomainModal").modal("toggle");
//
//         },
//         error: function (data) {
//             $('body').waitMe('hide');
//             console.log("ERROR: query sub domain failed :" + data);
//             $("#http-sub-domain").html("no sub domain");
//             $("#https-sub-domain").empty();
//             $("#subDomainModal").modal("toggle");
//         }
//     });
//
//
// }