(function ($) {
    'use strict';
    var clipboard = new Clipboard('.btn-clipboard');
    clipboard.on('success', function (e) {
        toastr.success('复制成功', 'Success', {positionClass: 'toast-top-right'});
        console.log(e);
    });
    clipboard.on('error', function (e) {
        toastr.error('复制失败', 'Error', {positionClass: 'toast-top-right'});
        console.log(e);
    });
})(jQuery);