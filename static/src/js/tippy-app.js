
var DOM = {
  performance: {
    btn: $('#performance-btn'),
    result: $('#performance-result'),
    test: $('#performance-test'),
    model: $('#performance-model')
  }
}

tippy('.flippy', {
  placement: 'right',
  animation: 'fade',
  arrowType: 'round',
  arrow: true,
  flipBehavior: ['right', 'bottom']
})

tippy('.dos', {
  placement: 'right',
  animation: 'fade',
  arrowType: 'round',
  arrow: true,
  flipBehavior: ['right', 'bottom']
})

// Performance section
var $perf = DOM.performance;
var jsperf = (function () {
  var i = 1
  var base = 100
  var counter = base
  var tippyTime = 0
  var tip

  return {
    updateModel: function () {
      var value = parseInt($perf.model.value) || 1
      $perf.btn.innerHTML = 'Append ' + value + (value === 1 ? ' element!' : ' elements!')

      if (tip) {
        tip.destroyAll()
      }

      this.reset(value)
    },
    reset: function (value) {
      i = 1
      tippyTime = 0
      counter = base = value
      $perf.test.innerHTML = $perf.result.innerHTML = ''
    },
    run: function () {
      for (i; i <= counter; i++) {
        var el = document.createElement('div')
        el.title = 'Performance test'
        el.className = 'test-element'
        el.innerHTML = i
        $perf.test.appendChild(el)
      }

      counter += base

      var t1 = performance.now()
      tip = tippy('.test-element', {
        hideOnClick: false,
        duration: 0,
        arrow: true,
        performance: true,
        animation: 'fade',
        updateDuration: 0
      })
      var t2 = performance.now()

      tippyTime += (t2 - t1)

      var innerHTML = '<p><strong>In total, Tippy instantiation has taken</strong> ' + tippyTime.toFixed(1) + ' milliseconds</p>' +
      '<p><strong>Current Tippy instantiation took</strong> ' + (t2 - t1).toFixed(1) + ' milliseconds</p>' +
      '<p><strong>Elements appended so far:</strong> ' + (counter - base) + '</p><hr>'

      $perf.result.innerHTML = innerHTML
    }
  }
})();


window.onload = function () {
    alert('Hey!!')
    //$perf.btn.addEventListener('click', jsperf.run)
}
