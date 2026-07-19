#!/bin/bash

# Add domain selection to the Generate Database card
sed -i '/<label>🌱 Rows per table<\/label>/i \            <div class="form-group">\n                <label>🏢 Business Domain</label>\n                <select id="dbDomain">\n                    <option value="ecommerce">🛒 E-Commerce</option>\n                    <option value="hr">👥 Human Resources</option>\n                    <option value="healthcare">🏥 Healthcare</option>\n                    <option value="finance">💰 Finance & Banking</option>\n                    <option value="education">🎓 Education</option>\n                </select>\n            </div>' templates/portal_complete.html

echo "✅ Portal updated with domain selection"
