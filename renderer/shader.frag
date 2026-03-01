in vec4 shadeColor;

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
}
