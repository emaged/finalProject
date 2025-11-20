import eslint from "@eslint/js";
import prettier from "eslint-config-prettier/flat";

export default [
    {
        languageOptions: {
            globals: { ...eslint.environments.browser.globals },
        },
    },
    eslint.configs.recommended,
    prettier,
];
