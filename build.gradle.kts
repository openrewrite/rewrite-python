plugins {
    id("org.openrewrite.build.recipe-library") version "latest.release"
    id("org.openrewrite.build.shadow") version "latest.release"
}
group = "org.openrewrite"
description = "Rewrite Python"

task("printIntellijDependencies", JavaExec::class) {
    mainClass.set("org.openrewrite.python.internal.CollectIntelliJDependenciesAsm")
    classpath = sourceSets["main"].runtimeClasspath
}

val latest = rewriteRecipe.rewriteVersion.get()
val lib = fileTree("lib")
dependencies {
    compileOnly("org.openrewrite:rewrite-test")

    implementation(platform("org.openrewrite:rewrite-bom:$latest"))
    implementation("org.openrewrite:rewrite-java")
    implementation(lib)

    implementation("org.jetbrains.kotlin:kotlin-stdlib-jdk8:1.7.10")
    runtimeOnly("org.jetbrains.kotlinx:kotlinx-coroutines-core-jvm:1.5.0")
    runtimeOnly("it.unimi.dsi:fastutil:8.5.2")
    runtimeOnly("com.google.guava:guava:31.1-jre")
    runtimeOnly("one.util:streamex:0.8.1")

    implementation("org.ow2.asm:asm:9.5")

    testImplementation("org.assertj:assertj-core:latest.release")
    testImplementation("org.junit.jupiter:junit-jupiter-api:latest.release")
    testImplementation("org.junit.jupiter:junit-jupiter-params:latest.release")
    testImplementation("org.openrewrite:rewrite-test")

    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:latest.release")
}

val shadowJar = tasks.named<com.github.jengelman.gradle.plugins.shadow.tasks.ShadowJar>("shadowJar") {
    from(lib)
    dependencies {
        include { _ -> false }
    }
}

tasks.withType<Javadoc> {
    options {
        this as CoreJavadocOptions
        addStringOption("Xdoclint:none", "-quiet")
    }
}
