window.onload = function () {
    'use strict';

    let Cropper = window.Cropper;
    let URL = window.URL || window.webkitURL;
    let container = document.querySelector('.img-container');
    let image = container.getElementsByTagName('img').item(0);
    let download = document.getElementById('download');
    let actions = document.getElementById('actions');
    let dataX = document.getElementById('dataX');
    let dataY = document.getElementById('dataY');
    let dataHeight = document.getElementById('dataHeight');
    let dataWidth = document.getElementById('dataWidth');
    let dataRotate = document.getElementById('dataRotate');
    let dataScaleX = document.getElementById('dataScaleX');
    let dataScaleY = document.getElementById('dataScaleY');
    let options = {
        /* 1 = restrict the crop box to not exceed the size of the canvas. */
        viewMode: 1,

        /* Force crop box aspect ratio (I don't want!): */
        // aspectRatio: 16 / 9,

        preview: '.img-preview',
        ready: function (e) {
            console.log(e.type);
        },
        cropstart: function (e) {
            console.log(e.type, e.detail.action);
        },
        cropmove: function (e) {
            console.log(e.type, e.detail.action);
        },
        cropend: function (e) {
            console.log(e.type, e.detail.action);
        },
        crop: function (e) {
            let data = e.detail;
            console.log(e);
            // dataX.value = Math.round(data.x);
            // dataY.value = Math.round(data.y);
            // dataHeight.value = Math.round(data.height);
            // dataWidth.value = Math.round(data.width);
            // dataRotate.value = typeof data.rotate !== 'undefined' ? data.rotate : '';
            // dataScaleX.value = typeof data.scaleX !== 'undefined' ? data.scaleX : '';
            // dataScaleY.value = typeof data.scaleY !== 'undefined' ? data.scaleY : '';
        },
        zoom: function (e) {
            console.log(e.type, e.detail.ratio);
        }
    };
    let cropper = new Cropper(image, options);
    let originalImageURL = image.src;
    let uploadedImageType = 'image/jpeg';
    let uploadedImageName = 'cropped.jpg';
    let uploadedImageURL;

    // Tooltip
    $('[data-toggle="tooltip"]').tooltip();

    // Buttons
    if (!document.createElement('canvas').getContext) {
        $('button[data-method="getCroppedCanvas"]').prop('disabled', true);
    }

    if (typeof document.createElement('cropper').style.transition === 'undefined') {
        $('button[data-method="rotate"]').prop('disabled', true);
        $('button[data-method="scale"]').prop('disabled', true);
    }

    // Download
    if (typeof download.download === 'undefined') {
        download.className += ' disabled';
        download.title = 'Your browser does not support download';
    }

    // Methods
    actions.querySelector('.docs-buttons').onclick = function (event) {
        let target = event.target;
        let cropped;
        let result;
        let input;
        let data;

        if (!cropper) {
            return;
        }

        while (target !== this) {
          if (target.getAttribute('data-method')) {
            break;
          }

          target = target.parentNode;
        }

        if (target === this || target.disabled || target.className.indexOf('disabled') > -1) {
            return;
        }

        data = {
          method: target.getAttribute('data-method'),
          target: target.getAttribute('data-target'),
          option: target.getAttribute('data-option') || undefined,
          secondOption: target.getAttribute('data-second-option') || undefined
        };

        cropped = cropper.cropped;

        if (data.method) {
            if (typeof data.target !== 'undefined') {
                input = document.querySelector(data.target);

                if (!target.hasAttribute('data-option') && data.target && input) {
                    try {
                        data.option = JSON.parse(input.value);
                    } catch (e) {
                        console.log(e.message);
                    }
                }
            }

            switch (data.method) {
                case 'rotate':
                    if (cropped && options.viewMode > 0) {
                        cropper.clear();
                    }
                    break;

                case 'getCroppedCanvas':
                  try {
                      data.option = JSON.parse(data.option);
                  } catch (e) {
                      console.log(e.message);
                  }

                  if (uploadedImageType === 'image/jpeg') {
                      if (!data.option) {
                          data.option = {};
                      }

                      data.option.fillColor = '#fff';
                  }
                  break;
            }

            result = cropper[data.method](data.option, data.secondOption);
            switch (data.method) {
                case 'rotate':
                  if (cropped && options.viewMode > 0) {
                    cropper.crop();
                  }

                  break;

                case 'scaleX':
                case 'scaleY':
                  target.setAttribute('data-option', -data.option);
                  break;

                case 'getCroppedCanvas':
                    if (result) {
                        // Bootstrap's Modal
                        $('#getCroppedCanvasModal').modal().find('.modal-body').html(result);

                        if (!download.disabled) {
                            download.download = uploadedImageName;
                            download.href = result.toDataURL(uploadedImageType);
                        }
                    }

                    break;

                case 'destroy':
                    cropper = null;
                    if (uploadedImageURL) {
                      URL.revokeObjectURL(uploadedImageURL);
                      uploadedImageURL = '';
                      image.src = originalImageURL;
                    }
                   break;
            }

            if (typeof result === 'object' && result !== cropper && input) {
                try {
                    input.value = JSON.stringify(result);
                } catch (e) {
                    console.log(e.message);
                }
            }
        }
    };

    document.body.onkeydown = function (event) {
        let e = event;

        if (e.target !== this || !cropper || this.scrollTop > 300) {
              return;
        }

        switch (e.keyCode) {
            case 37:
                e.preventDefault();
                cropper.move(-1, 0);
                break;

            case 38:
                e.preventDefault();
                cropper.move(0, -1);
                break;

            case 39:
                e.preventDefault();
                cropper.move(1, 0);
                break;

            case 40:
                e.preventDefault();
                cropper.move(0, 1);
                break;
        }
    };

    // Import image
    let inputImage = document.getElementById('inputImage');

    if (URL) {
        inputImage.onchange = function () {
            let files = this.files;
            let file;

            if (cropper && files && files.length) {
                 file = files[0];

                if (/^image\/\w+/.test(file.type)) {
                    uploadedImageType = file.type;
                    uploadedImageName = file.name;

                    if (uploadedImageURL) {
                        URL.revokeObjectURL(uploadedImageURL);
                    }

                    image.src = uploadedImageURL = URL.createObjectURL(file);
                    cropper.destroy();
                    cropper = new Cropper(image, options);
                            inputImage.value = null;
                } else {
                    window.alert('Please choose an image file.');
                }
            }
        };
    } else {
      inputImage.disabled = true;
      inputImage.parentNode.className += ' disabled';
    }
};
