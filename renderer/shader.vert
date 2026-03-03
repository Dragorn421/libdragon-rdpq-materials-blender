vec3 linearToGamma(in vec3 color) {
    return mix(
        color * 12.92,
        1.055 * pow(color, vec3(1.0 / 2.4)) - 0.055,
        step(0.0031308, color)
    );
}

void main()
{
    gl_Position = inState.matMVP * vec4(inPos, 1.0);
    float i = max(0, dot(normalize(mat3(inState.matMV) * inNormal), vec3(0, 0, 1)));
    shadeColor = inColor * vec4(i, i, i, 1.0);
    shadeColor.rgb = linearToGamma(shadeColor.rgb);
    if ((inState.validInputs & VALID_IN_UV) != 0)
        uv = inUV;
}
