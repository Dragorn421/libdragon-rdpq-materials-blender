uniform int inValidInputs;
uniform sampler2D inTex0;

in vec4 shadeColor;
in vec2 uv;

out vec4 FragColor;

vec3 gammaToLinear(in vec3 color) {
    return mix(
        color * (1.0 / 12.92),
        pow((color + 0.055) * (1.0 / 1.055), vec3(2.4)),
        step(0.04045, color)
    );
}

void main() 
{
    FragColor = shadeColor;
    FragColor.rgb = gammaToLinear(FragColor.rgb);
    if ((inValidInputs & VALID_IN_TEX0) != 0 && (inValidInputs & VALID_IN_UV) != 0)
        FragColor.rgb *= texture(inTex0, uv).rgb;
}
