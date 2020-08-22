/**
 * The entire contents of JavaScript modules are automatically in strict mode,
 * with no statement needed to initiate it.
 *
 * Source:
 *
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Strict_mode
 */
import {HqfCropper} from "./main-cropper.js";

export class Hqf {
    constructor(ajax_url, img_url) {
        /* Cropper functions */
        let $img = $($('.img-container img')[0]);
        $img.attr('src', img_url).on('load', function () {
            let c = new HqfCropper();
            $('#btn-text-detect').on('click', () => {
                let data = {img: c.cropper.getCroppedCanvas().toDataURL(), };
                $.ajax({
                    url: ajax_url,
                    method: 'post',
                    data: data,
                }).done(function (result) {
                    console.log(result);
                });
            });
        });


        /* Other functions */
        /* Focus the first element with attribute 'focused': */
        let $to_be_focused = $('[focused]');
        if ($to_be_focused.length) {
            $to_be_focused.get(0).focus();
        } else {
            /* Not found? Focus the first item of the first form found: */
            /* Small timeout to make sure all forms are drawn: */
            setTimeout(function () {
                $('form:first *:input[type!=hidden]:first').get(0).focus();
            }, 200);
        }

        let remove = function (event) {
            event.preventDefault();
            $(this).closest('.multiple-field-item').remove()
        };
        let hover = function () {
            $(this).hover(function () {
                $(this).find('.button-appear-on-hover').stop().fadeIn();
            }, function () {
                $(this).find('.button-appear-on-hover').stop().fadeOut();
            });
        };
        $('.add-item-multiple-field').click(function (event) {
            event.preventDefault();
            let target = $(this).data('target'),
                parent = $("#" + target)[0],
                template = $("#" + target + "> .template-item")[0],
                item=$(template.outerHTML);  /* (!) duplicate item */
            item.find('.remove-item-multiple-field').click(remove);
            item.removeClass('template-item'); /* make it real */
            hover.apply(item);
            parent.append(item[0]);
        });
        $('.remove-item-multiple-field').click(remove);
        $('.multiple-field-item').each(function() {
            hover.apply(this)
        });
    }
}
