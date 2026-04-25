-- Shortcode to embed a RevealJS slide deck as an iframe.
-- Usage: {{< slides lecture-1 >}}
-- Renders: an iframe pointing to slides/<name>.html wrapped in responsive CSS classes.

return {
  ["slides"] = function(args)
    local name = pandoc.utils.stringify(args[1])
    local html = '<div class="responsive-container">\n'
      .. '  <iframe class="responsive-iframe" src="../slides/'
      .. name
      .. '.html" allowfullscreen></iframe>\n'
      .. '</div>'
    return pandoc.RawInline("html", html)
  end
}
