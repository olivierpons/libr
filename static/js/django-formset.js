$(() => {
    "use strict";
    /* formsetGet = to get the "current" formset, change this if you change the
     * formset container (currently it's in a div with class "form-group"):
     */
    function formsetGet() {
        /* this = already a jQuery element, dont do again "$(this)": */
        console.log(this.closest('.form-group').get(0));
        return this.closest('.form-group');
    }
    function formsetClone() {
        let $this = $(this),
            prefix = $this.attr('form-prefix') || 'form',
            $last_formset = formsetGet.call($this).find('.formset-row:last'),
            $new_el = $last_formset.clone(true).show(),
            $total_forms = $('#id_' + prefix + '-TOTAL_FORMS'),
            total = $total_forms.val(),
            total_search = '-' + (total-1) + '-',
            total_replace = '-' + total + '-';
        $new_el
            .find(':input')
            .not(':button, [type=button], [type=submit], [type=reset]')
            .each(function() {
                let name = $(this)
                    .attr('name')
                    .replace(total_search, total_replace);
                let id = 'id_' + name;
                $(this)
                    .attr({'name': name, 'id': id})
                    .val('')
                    .removeAttr('checked');
            });
        $new_el.find('label').each(function() {
            let $for_el = $(this).attr('for');
            if ($for_el) {
                $for_el = $for_el.replace(total_search, total_replace);
                $(this).attr({'for': $for_el});
            }
        });
        total++;
        $total_forms.val(total);
        $last_formset.after($new_el);
        return false;
    }
    function formsetUpdateIndexes(el, prefix, idx) {
        let id_regex = new RegExp('(' + prefix + '-\\d+)');
        let replacement = prefix + '-' + idx;
        if ($(el).attr("for")) {
            $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
        }
        if (el.id) {
            el.id = el.id.replace(id_regex, replacement);
        }
        if (el.name) {
            el.name = el.name.replace(id_regex, replacement);
        }
    }
    function formsetRemove() {
        let $this = $(this),
            $formset = formsetGet.call($this),
            prefix = $this.attr('form-prefix') || 'form',
            $el_total_forms = $('#id_' + prefix + '-TOTAL_FORMS');
        $this.closest('.formset-row').remove();
        let $form_rows = $formset.find('.formset-row');
        $el_total_forms.val($form_rows.length);
        for (let i=0, formCount=$form_rows.length; i<formCount; i++) {
            $($form_rows.get(i)).find(':input').each(function() {
                formsetUpdateIndexes(this, prefix, i);
            });
        }
        return false;
    }
    $('button.formset-add').on('click', function (e) {
        e.preventDefault();
        formsetClone.call(this);
        return false;
    });
    $('form').submit(function () {
        $(this)
            .find('.formset-row:hidden')
            .find('.formset-remove').each(function () {
                formsetRemove.call($(this));
            })
    });
    $('button.formset-remove').on('click', function (e) {
        e.preventDefault();
        formsetRemove.call(this);
        return false;
    });
});
