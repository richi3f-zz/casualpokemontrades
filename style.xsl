<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="html" encoding="utf-8" doctype-system="about:legacy-compat" indent="yes" />
<xsl:template match="/">
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=360, initial-scale=1" />
    <title>/r/CasualPokemonTrades Flair Bot</title>
    <link rel="stylesheet" href="style.css" />
</head>

<body>
    <main role="main">
        <article>
            <header role="banner">
                <h1><a href="http://reddit.com/r/casualpokemontrades">/r/CasualPokemonTrades</a> Flair Bot</h1>
            </header>
            <form action="/" method="post">
                <label for="ign">In-Game Name</label>
                <input id="ign" name="ign" type="text" />
                
                <label for="fc">Friend Code</label>
                <input id="fc" name="fc" type="text" placeholder="0000-0000-0000" maxlength="14" />
                
                <label for="pkmn">Pokémon</label>
                <select id="pkmn" name="pkmn">
                    <option selected="selected"></option>
                    <xsl:for-each select="PkmnDbData/Generation">
                        <xsl:variable name="initial" select="Count" />
                        <optgroup>
                            <xsl:attribute name="label">
                                <xsl:value-of select="Region" />
                            </xsl:attribute>
                            <xsl:for-each select="Pkmn">
                                <xsl:variable name="position" select="$initial + position()"/>
                                <option>
                                    <xsl:choose>
                                        <xsl:when test="Class">
                                            <xsl:attribute name="value">
                                                <xsl:value-of select="Class" />
                                            </xsl:attribute>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <xsl:attribute name="value">
                                                <xsl:value-of select="translate(Name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZé', 'abcdefghijklmnopqrstuvwxyze')" />
                                            </xsl:attribute>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                    <xsl:value-of select="concat(format-number($position,'000'), '. ', Name)" />
                                </option>
                                <xsl:for-each select="Form">
                                    <option>
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="Class" />
                                        </xsl:attribute>
                                        <xsl:value-of select="concat(format-number($position,'000'), '. ', Name)" />
                                    </option>
                                </xsl:for-each>
                            </xsl:for-each>
                        </optgroup>
                    </xsl:for-each>
                </select>
                
                <label for="name">Reddit Username</label>
                <input id="name" name="name" type="text" />
                <section id="preview">
                    <h2>Preview</h2>
                    <p><span class="flair"><span class="fc">0000-0000-0000</span> | <span class="ign">???</span></span></p>
                </section>
                <input type="submit" value="Submit" />
            </form>
        </article>
    </main>
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
    <script>
<![CDATA[
function enableSubmitButton() {
    var fc = $("#fc").val();
    if ($("#ign").val().length > 0 && $("#name").val().length > 0 && $("#pkmn")[0].selectedIndex > 0 && /^\d{4}-\d{4}-\d{4}$/.test(fc)) {
        $("[type=submit]").removeAttr("disabled").removeAttr("title");
    } else {
        $("[type=submit]").attr("disabled", "disabled").attr("title", "Please fill all the fields and enter a valid Friend Code.");
    }
}

$(document).ready(function() {
    $("[type=submit]").attr("disabled", "disabled").attr("title", "Please fill all the fields and enter a valid Friend Code.");
    
    var propertyChangeUnbound = false;
    $("input[id]").on("propertychange", function(e) {
        if (e.originalEvent.propertyName == "value") {
            enableSubmitButton();
        }
    });

    $("input[id]").on("input", function() {
        if (!propertyChangeUnbound) {
            $("input").unbind("propertychange");
            propertyChangeUnbound = true;
        }
        enableSubmitButton();
    });
    
    $('select').change(function () {
        enableSubmitButton();
        $('.flair').removeAttr('class').addClass('flair flair-' + $(this).val());
    });
    
    $('#ign').keyup(function() {
        $('.ign').text($(this).val());
    });
    
    $('#fc').keyup(function() {
        var foo = $(this).val().split("-").join(""); // remove hyphens
        if (foo.length > 0) {
            foo = foo.match(new RegExp('.{1,4}', 'g')).join("-");
        }
        $(this).val(foo);
        $('.fc').text(foo);
    });
});
]]>
    </script>
</body>
</html>

</xsl:template>
</xsl:stylesheet>
