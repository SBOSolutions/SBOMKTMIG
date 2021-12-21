odoo.define('matrix_stock.section_and_note_widget', function (require) {

    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var _t = core._t;
    var qweb = core.qweb;
    var fieldRegistry = require('web.field_registry');
    require('account.section_and_note_backend');
    
    var SectionAndNoteFieldOne2Many = fieldRegistry.get('section_and_note_one2many');
    
    SectionAndNoteFieldOne2Many.include({
        custom_events: _.extend({}, SectionAndNoteFieldOne2Many.prototype.custom_events, {
            open_matrix: '_openMatrix',
        }),
    
        /**
         * Triggers Matrix Dialog opening
         *
         * @param {String} jsonInfo matrix dialog content
         * @param {integer} productTemplateId product.template id
         * @param {editedCellAttributes} list of product.template.attribute.value ids
         *  used to focus on the matrix cell representing the edited line.
         *
         * @private
        */
        _openMatrixConfigurator: function (jsonInfo, productTemplateId, editedCellAttributes) {
            var self = this;
            var infos = JSON.parse(jsonInfo);
            debugger
            var MatrixDialog = new Dialog(this, {
                title: _t('Choose Product Variants'),
                size: 'extra-large', // adapt size depending on matrix size?
                $content: $(qweb.render(
                    'product_matrix.matrix', {
                        header: infos.header,
                        rows: infos.matrix,
                        stock_display: self.recordData.display_stock_matrice ,
                    }
                )),
                buttons: [
                    {text: _t('Confirm'), classes: 'btn-primary', close: true, click: function (result) {
                        var $inputs = this.$('.o_matrix_input');
                        var matrixChanges = [];
                        _.each($inputs, function (matrixInput) {
                            if (matrixInput.value && matrixInput.value !== matrixInput.attributes.value.nodeValue) {
                                matrixChanges.push({
                                    qty: parseFloat(matrixInput.value),
                                    ptav_ids: matrixInput.attributes.ptav_ids.nodeValue.split(",").map(function (id) {
                                          return parseInt(id);
                                    }),
                                });
                            }
                        });
                        if (matrixChanges.length > 0) {
                            self._applyGrid(matrixChanges, productTemplateId);
                        }
                    }},
                    {text: _t('Close'), close: true},
                ],
            }).open();
    
            MatrixDialog.opened(function () {
                if (editedCellAttributes.length > 0) {
                    var str = editedCellAttributes.toString();
                    MatrixDialog.$content.find('.o_matrix_input').filter((k, v) => v.attributes.ptav_ids.nodeValue === str)[0].focus();
                } else {
                    MatrixDialog.$content.find('.o_matrix_input:first()').focus();
                }
            });
        },
    
    });
    
    return SectionAndNoteFieldOne2Many;
    
    });
    